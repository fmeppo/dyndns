import boto3, pprint, logging, hashlib

secret_nonce = "hardcode a secret string here"

def lambda_handler(event, context):
    defaults = {
        'fqdn': 'host.example.com',
        'token': 'invalid',
        'zoneid': 'invalid',
        'ttl': 300,
        'ipv4': None,
        'ipv6': None
        }
    pp = pprint.PrettyPrinter(indent=4)
    ret = { 'headers': {'Content-Type': 'text/plain'} }
    if not event.has_key('queryStringParameters') or event['queryStringParameters'] == None:
        ret['body'] = "Missing query string"
        ret['statusCode'] = "500"
    elif not event['queryStringParameters'].has_key('token') or not event['queryStringParameters'].has_key('fqdn'):
        ret['body'] = "Missing essential parameters"
        ret['statusCode'] = "501"
    else:
        ret['body'] = "Hello!"
        ret['statusCode'] = "200"

        if event.has_key('requestContext') and event['requestContext'].has_key('identity'):
            defaults['ipv4'] = event['requestContext']['identity']['sourceIp']
        
        ret['body'] = ret['body'] + pp.pformat(defaults)

        for key in defaults.keys():
            if event['queryStringParameters'].has_key(key):
                defaults[key] = event['queryStringParameters'][key]
    
        change_batch = { 'Changes': [] }
        if defaults['ipv4'] != None:
            change_batch['Changes'].append(
                { 'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': defaults['fqdn'],
                    'Type': 'A',
                    'TTL': defaults['ttl'],
                    'ResourceRecords': [ { 'Value': defaults['ipv4'] } ]
                    } } )

        if defaults['ipv6'] != None:
            change_batch['Changes'].append(
                { 'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': defaults['fqdn'],
                    'Type': 'AAAA',
                    'TTL': defaults['ttl'],
                    'ResourceRecords': [ { 'Value': defaults['ipv6'] } ]
                    } } )
        ret['body'] = ret['body'] + '\n' + pp.pformat(change_batch)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.info("hello there")
        
        # Validate permissions before trying to send
        if hashlib.sha256(defaults['fqdn'] + defaults['zoneid'] + secret_nonce).hexdigest() == defaults['token']:
            try:
                client = boto3.client('route53')
                response = client.change_resource_record_sets(HostedZoneId=defaults['zoneid'], ChangeBatch=change_batch)
            except Exception, e:
                ret['body'] = ret['body'] + "\nEncountered error: " + str(e)
                return ret
            ret['body'] = ret['body'] + '\n' + pp.pformat(response)

            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                ret['body'] = ret['body'] + '\n' + response['ChangeInfo']['Status']
            ret['statusCode'] = response['ResponseMetadata']['HTTPStatusCode']
        else:
            # Invalid token
            ret['body'] = ret['body'] + '\nInvalid token'
            ret['statusCode'] = 403

    return ret
