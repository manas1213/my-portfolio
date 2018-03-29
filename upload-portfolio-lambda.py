import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:299168389433:deployPortolioTopic')

    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        portfolio_bucket = s3.Bucket('myportfolio.manasmohanty.info')
        build_bucket = s3.Bucket('portfoliobuild.manas.info')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfolioBuild.zip',portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,
                ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print 'Job Done !!!'
        topic.publish(Subject='Portfolio', Message="Portfolio Deployed Successfully")

    except:
        topic.publish(Subject='Portfolio Deployment Failed', Message="Portfolio was not Deployed Successfully")
        raise

    return 'Hello from Lambda'
