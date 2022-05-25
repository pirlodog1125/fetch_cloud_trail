# -*- coding: utf-8 -*-
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'site-packages'))
import botocore
import boto3
from datetime import datetime, timedelta, timezone
import json
from pprint import pprint
import time
import urllib
import urllib.request
from myutil import *
from myboto3util import *
import uuid

cloudtrail = boto3.client('cloudtrail')

def lambda_handler(event, context):
    pprint(event)

    outdir = f'out/{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    filepath = f'{outdir}/out.log'
    os.makedirs(outdir, exist_ok=True)

    max = 100
    NextToken = None
    start = datetime(2021, 4, 15, 0, 0, 0)
    end   = datetime(2021, 4, 15, 23, 59, 59)
    while max > 0:
        if NextToken is not None:
            response = cloudtrail.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'EventName',
                        'AttributeValue': 'DeleteLogStream'
                    },
                ],
                StartTime=start,
                EndTime=end,
                MaxResults=100,
                NextToken=NextToken,
            )
        else:
            response = cloudtrail.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'EventName',
                        'AttributeValue': 'DeleteLogStream'
                    },
                ],
                StartTime=start,
                EndTime=end,
                MaxResults=100,
            )

        #print(response)

        Events = response['Events']
        NextToken = response.get('NextToken')
        for an_event in Events:
            #pprint(an_event)

            Username = an_event['Username']
            EventTime = an_event['EventTime']

            CloudTrailEvent = an_event['CloudTrailEvent']
            CloudTrailEvent = json.loads(CloudTrailEvent)
            #print(CloudTrailEvent)

            requestParameters = CloudTrailEvent['requestParameters']

            print('**************************************************')
            print('Resource', requestParameters)
            print('Username', Username)
            print('Date', EventTime)

            with open(filepath, mode='a') as f:
                f.write(f'Resource: {requestParameters} / Username: {Username} / Date: {EventTime}')
                f.write('\n')

        print('NextToken', NextToken)

        if NextToken is None:
            break

        max += -1

    return {}