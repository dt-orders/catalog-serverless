
aws lambda publish-layer-version --layer-name catalog-function-prereq \
--description "Requirements for Catalog lambdas" \
--zip-file fileb://package/catalog-python-prereq.zip \
--compatible-runtimes python3.10 \
--compatible-architectures "x86_64"

#(collect LayerVersionArn)

# need vpc, security groups for connectivity to RDS!!!

# populate environment variables with appropriate values from rds creation

aws lambda create-function \
    --function-name findByNameContains \
    --runtime python3.10 \
    --zip-file fileb://package/findByNameContains.zip \
    --handler lambda_function.lambda_handler \
    --layers "${LAYER_VERSION_ARN}" \
    --role "${SQS_ROLE_ARN}" \
    --environment "Variables={DB_NAME=${DB_NAME},PASSWORD=${PASSWORD},RDS_HOST=${RDS_HOST},USER_NAME=${USER_NAME}}"

aws lambda add-permission \
    --function-name findByNameContains \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type "NONE" \
    --statement-id url

aws lambda create-function-url-config \
    --function-name findByNameContains \
    --auth-type NONE