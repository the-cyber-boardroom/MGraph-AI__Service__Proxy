import os

from mgraph_ai_service_proxy.config import LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS

if os.getenv('AWS_REGION'):  # only execute if we are not running inside an AWS Lambda function

    from osbot_aws.aws.lambda_.boto3__lambda import load_dependencies       # using the lightweight file (which only has the boto3 calls required to load_dependencies)

    load_dependencies(LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS)

    def clear_osbot_modules():                            # todo: add this to load_dependencies method, since after it runs we don't need the osbot_aws.aws.lambda_.boto3__lambda
        import sys
        for module in list(sys.modules):
            if module.startswith('osbot_aws'):
                del sys.modules[module]

    clear_osbot_modules()


from mgraph_ai_service_proxy.fast_api.Service__Fast_API import Service__Fast_API

with Service__Fast_API() as _:
    try:                                            # todo: add better support for handling these _.setup() errors
        _.setup()
        setup_error = None
    except Exception as e:
        setup_error = { "error"  : "Setup failed",
                        "message": str(e)        }

    handler = _.handler()
    app     = _.app()

def run(event, context=None):
    if setup_error:                                 # todo: add better support for handling these _.setup() errors
        return setup_error
    return handler(event, context)

