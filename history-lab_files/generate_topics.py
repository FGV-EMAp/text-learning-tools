description = """
REQUIREMENTS: This script requires rosetta to be installed at _exactly_ the
following commit:

    b0bd1da9cd6325aa040c11c37edd3429ac01ea93

This is not ideal, but will hopefully be eventually resolved.

Generate Topics
---------------

This script generates topic data for a table of documents in a mysql database.
The database is assumed to have a table called `docs` with two fields: `id` and
`body`. The body field is parsed as text and topic modeling is done on it.

After topic modeling, the script creates 4 topic tables in the database of the
following form (table name, the fields and their types):

    topic_doc
        * doc_id - str
        * topic_id - int
        * topic_score - float

    topics
        * id - int
        * title - str

    topic_token
        * token_id - int
        * topic_id - int
        * token_score - float

    tokens
        * id - int
        * value - str

CAUTION: In its current form, this script is _destructive_. I.e. if any
tables by the names `topic_doc`, `topics`, `topic_token`, or `tokens` exist,
then those tables will be dropped and re-generated.
"""

import os
import yaml
import tempfile
import argparse
import pymysql
import shutil

#Clone LemmaSynsetTokenizer.py from processing/common/util  
from LemmaSynsetTokenizer import LemmaSynsetTokenizer

from rosetta.text.database_streamers import MySQLStreamer
from rosetta.text.text_processors import VWFormatter, SFileFilter
from rosetta.text.streaming_filters import get_min_token_filter
from rosetta.text.vw_helpers import LDAResults


def main(dbinfo, tmpdir, limit=None, verbose=False):
    if verbose:
        print "Running on {0} database.\n".format(dbinfo['database'])
    # Prepare database tables where final data will be uploaded.
    with pymysql.connect(autocommit=True, **dbinfo) as cursor:
        createschema(cursor)

    if verbose:
        print "Tokenizing data..."
    stopwords = set()
    tokenizer = LemmaSynsetTokenizer(stopwords)
    streamer = getstreamer(dbinfo, tokenizer, limit)

    alltokenspath = os.path.join(tmpdir, "alltokens.vw")
    with open(alltokenspath, "w") as outfile:
        streamer.to_vw(outfile)

    if verbose:
        print "Filtering data..."
    sff = SFileFilter(VWFormatter())
    sff.load_sfile(alltokenspath)
    sff.filter_extremes(doc_freq_min=5,
                        doc_fraction_max=0.8,
                        token_score_quantile_min=0.01,
                        token_score_quantile_max=0.99)
    sff.compactify()
    sffpath = os.path.join(tmpdir, 'sff.pkl')
    sff.save(sffpath)
    tokenspath = os.path.join(tmpdir, "tokens.vw")
    filters = [get_min_token_filter(20)]
    sff.filter_sfile(alltokenspath, tokenspath, min_tf_idf=5, filters=filters)
    bitprecision = sff.bit_precision_required
    sff = None

    if verbose:
        print "Running vw LDA..."
    runlda(tmpdir=tmpdir, bitprecision=bitprecision)

    if verbose:
        print "Getting topic data..."
    doctopicdata, topicdata, topictokendata, tokendata = gettopicdata(tmpdir=tmpdir)

    if verbose:
        print "Uploading topic data to database..."
    with pymysql.connect(**dbinfo) as cursor:
        inserttopicdata(cursor, doctopicdata, topicdata, topictokendata, tokendata)
    if verbose:
        print "" # For formatting clarity.
    addkeystoschema(cursor)

def cli():
    parser = argparse.ArgumentParser(
                description=description,
                formatter_class=argparse.RawTextHelpFormatter,
                add_help=False)

    # Override default help argument so that only --help (and not -h) can call
    # help
    parser.add_argument(
        '--help',
        action='help',
        default=argparse.SUPPRESS,
        help=argparse._('show this help message and exit'))

    parser.add_argument(
        'database',
        metavar='DATABASE',
        type=str,
        help='Name source database.')

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Print detailed move information.')

    parser.add_argument(
        '-h',
        "--host",
        required=False,
        type=str,
        default='127.0.0.1',
        help="Default: '127.0.0.1'")

    parser.add_argument(
        '-u',
        "--user",
        required=False,
        type=str,
        default='root',
        help="Default: 'root'")

    parser.add_argument(
        '-p',
        "--password",
        metavar='PW',
        required=False,
        type=str,
        default='',
        help="Default: ''")

    parser.add_argument(
        "-l", "--limit",
        metavar='LIM',
        type=int,
        default=0,
        help="Limit number of docs. Meant for debugging.")

    args = parser.parse_args()

    if args.database not in ['declassification_frus',
                             'declassification_statedeptcables',
                             'declassification_ddrs',
                             'declassification_kissinger']:
        err_msg = ("Database must be one of frus, statedeptcables, ddrs or "
                   "kissinger.")
        raise Exception(err_msg)

    dbinfo = {
        'host': args.host,
        'user': args.user,
        'passwd': args.password,
        'database': args.database}

    if args.limit == 0:
        args.limit = None

    return (dbinfo, args.limit, args.verbose)

def inserttopicdata(cursor, doctopicdata, topicdata, topictokendata, tokendata,
                    verbose=True):
    # Populate the topic table.
    topicquery = "INSERT INTO topics VALUES (%s, %s);"
    if verbose:
        print "Creating table topics..."
    cursor.executemany(topicquery, topicdata)
    cursor.connection.commit()
    # Populate the doctopic table.
    batchsize = len(doctopicdata) / 10
    offset = 0
    doctopicquery = "INSERT INTO topic_doc VALUES (%s, %s, %s);"
    if verbose:
        print "Creating table topic_doc..."
    while offset < len(doctopicdata):
        data = doctopicdata[offset: offset + batchsize]
        cursor.executemany(doctopicquery, data)
        cursor.connection.commit()
        offset += batchsize
        if verbose:
            progress = 100 * float(offset) / len(doctopicdata)
            progress = min(100.0, progress)
            print "\tFinished uploading %.1f%% of data..." % progress
    # Populate the topic token table.
    batchsize = len(topictokendata) / 10
    offset = 0
    topictokenquery = "INSERT INTO topic_token VALUES (%s, %s, %s);"
    if verbose:
        print "Creating table topic_token..."
    while offset < len(topictokendata):
        data = topictokendata[offset: offset + batchsize]
        cursor.executemany(topictokenquery, data)
        cursor.connection.commit()
        offset += batchsize
        if verbose:
            progress = 100 * float(offset) / len(topictokendata)
            progress = min(100.0, progress)
            print "\tFinished uploading %.1f%% of data..." % progress
    # Populate the token table.
    batchsize = len(tokendata) / 10
    offset = 0
    tokenquery = "INSERT INTO tokens VALUES (%s, %s);"
    if verbose:
        print "Creating table tokens..."
    while offset < len(tokendata):
        data = tokendata[offset: offset + batchsize]
        cursor.executemany(tokenquery, data)
        cursor.connection.commit()
        offset += batchsize
        if verbose:
            progress = 100 * float(offset) / len(tokendata)
            progress = min(100.0, progress)
            print "\tFinished uploading %.1f%% of data..." % progress


def gettopicdata(tmpdir="/tmp", topicspath=None, predictionspath=None,
                  sffpath=None, numtopics=100, topiccutoff=3, titlecutoff=3):
    # Set defaults if necessary.
    if topicspath is None:
        topicspath = os.path.join(tmpdir, "topics.dat")
    if predictionspath is None:
        predictionspath = os.path.join(tmpdir, "predictions.dat")
    if sffpath is None:
        sffpath = os.path.join(tmpdir, 'sff.pkl')
    # Load and normalize LDA topic data.
    lda = LDAResults(topicspath, predictionspath, sffpath, numtopics)
    alltopics = lda.pr_topic_doc
    alltopics = alltopics.div(alltopics.sum(axis=1), axis=0)
    # Generate topic keys.
    topicnames = alltopics.columns
    topicidtoname = dict(enumerate(topicnames))
    topicnametoid = {name: topicid
                     for topicid, name in topicidtoname.iteritems()}
    # Extract doctopic data.
    doctopicdata = []
    docids = alltopics.index
    for docid in docids:
        doc = alltopics.ix[docid]
        doc.sort(ascending=False)
        toptopics = doc[:topiccutoff]
        for topicname, topicscore in toptopics.iteritems():
            topicid = topicnametoid[topicname]
            # Topicscore is type numpy.float64 by default which pymysql cannot
            # handle. Hence we convert it to float.
            topicscore = float(topicscore)
            doctopicdata.append((docid, topicid, topicscore))
    # Extract topic title data.
    topicdata = []
    for topicname in topicnames:
        topicid = topicnametoid[topicname]
        tokenscores = lda.pr_token_g_topic[topicname].copy()
        tokenscores.sort(ascending=False)
        words = ', '.join(tokenscores.keys()[:titlecutoff])
        topictitle = '{' + words + '}'
        topicdata.append((topicid, topictitle))
    # Extract topic score data.
    tokens = lda.pr_token_g_topic[topicnames[0]].index
    tokenmapping = dict(enumerate(tokens))
    tokenmapping = {a: b for b, a in tokenmapping.iteritems()}
    # Extract topic token data.
    topictokendata = []
    for topicname in topicnames:
        topicid = topicnametoid[topicname]
        tokenscores = lda.pr_token_g_topic[topicname].copy()
        tokenscores.sort(ascending=False)
        for token, tokenscore in tokenscores.iteritems():
            tokenid = tokenmapping[token]
            # Tokenscore is type numpy.float64 by default which pymysql cannot
            # handle. Hence we convert it to float.
            tokenscore = float(tokenscore)
            topictokendata.append((tokenid, topicid, tokenscore))
    # Extract token data.
    tokendata = {a: b for b, a in tokenmapping.iteritems()}.items()
    return doctopicdata, topicdata, topictokendata, tokendata


def addkeystoschema(cursor):
    query = """
    ALTER TABLE topics ADD PRIMARY KEY (id);
    ALTER TABLE topic_doc
        ADD INDEX doc_id_topic_score (doc_id, topic_score);
    ALTER TABLE topic_doc
        ADD INDEX topic_score_topic_id (topic_score, topic_id);
    """
    cursor.execute(query)


def createschema(cursor):
    query = """
    DROP TABLE IF EXISTS topic_doc;
    DROP TABLE IF EXISTS topics;
    DROP TABLE IF EXISTS topic_token;
    DROP TABLE IF EXISTS tokens;

    CREATE TABLE topics (
        id SMALLINT,
        title TEXT NOT NULL)
    CHARACTER SET utf8
    COLLATE utf8_general_ci
    ;

    CREATE TABLE topic_doc (
        doc_id VARCHAR(31) NOT NULL,
        topic_id SMALLINT NOT NULL,
        topic_score FLOAT NOT NULL)
    CHARACTER SET utf8
    COLLATE utf8_general_ci
    ;

    CREATE TABLE topic_token (
        token_id INT NOT NULL,
        topic_id SMALLINT NOT NULL,
        token_score FLOAT NOT NULL)
    CHARACTER SET utf8
    COLLATE utf8_general_ci
    ;

    CREATE TABLE tokens (
        id INT,
        value TEXT NOT NULL)
    CHARACTER SET utf8
    COLLATE utf8_general_ci
    ;
    """
    cursor.execute(query)


def runlda(tmpdir="/tmp", topicspath=None, predictionspath=None,
           tokenspath=None, numtopics=100, numpasses=20, ldarho=0.1,
           ldaalpha=1, bitprecision=16):
    if topicspath is None:
        topicspath = os.path.join(tmpdir, "topics.dat")
    if predictionspath is None:
        predictionspath = os.path.join(tmpdir, "predictions.dat")
    if tokenspath is None:
        tokenspath = os.path.join(tmpdir, 'tokens.vw')
    # Next run LDA.
    cmd = """
    cd %(tmpdir)s
    rm -f *.cache
    vw --lda %(numtopics)s \\
       --cache_file tokens.cache \\
       --passes %(numpasses)s \\
       -p %(predictionspath)s \\
       --readable_model %(topicspath)s \\
       --bit_precision %(bitprecision)s \\
       --lda_rho %(ldarho)s \\
       --lda_alpha %(ldaalpha)s \\
       --quiet \\
       %(tokenspath)s
    """ % {
        'tmpdir': tmpdir,
        'predictionspath': predictionspath,
        'topicspath': topicspath,
        'tokenspath': tokenspath,
        'numtopics': numtopics,
        'numpasses': numpasses,
        'ldarho': ldarho,
        'ldaalpha': ldaalpha,
        'bitprecision': bitprecision}
    os.system(cmd)


def getstreamer(dbinfo, tokenizer, limit=None):
    query = """
    SELECT
        id as doc_id,
        body as text
    FROM docs
    WHERE
        body IS NOT NULL
        AND body != ''
    LIMIT
    ;
    """
    if limit is not None:
        query = query.replace("LIMIT", "LIMIT %s" % limit)
    else:
        query = query.replace("LIMIT", "")
    db_setup = {
        'host' : dbinfo['host'],
        'user': dbinfo['user'],
        'password': dbinfo['passwd'],
        'database': dbinfo['database'],
        'query': query}
    streamer = MySQLStreamer(db_setup=db_setup, tokenizer=tokenizer)
    return streamer

if __name__ == '__main__':
    #with open(os.path.join(os.environ['HOME'], '.declass_rw')) as f:
    #    dbinfo = yaml.load(f)

    dbinfo, limit, verbose = cli()

    tmpdir = tempfile.mkdtemp()
    main(dbinfo, tmpdir, limit, verbose)
    shutil.rmtree(tmpdir)
