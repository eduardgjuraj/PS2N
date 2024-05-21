RESOURCE_GROUP_NAME='ps-python-arduino'
APP_SERVICE_NAME='ps-python-arduino-EDY'

az webapp deployment source config-local-git \
    --name $APP_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP_NAME \
    --query "{Username:$ps-python-arduino-EDY, Password:MXMwQ0GCH09QBKwhjFCDoPAMnbvrdLTsgusmDHj34wTrSA43T0oPMZiWWLRJ}" \
    --output table
    