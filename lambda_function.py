#AWS enabled REST API Application

import json
import boto3
import os
import time

s3 = boto3.client('s3')

BUCKET_NAME = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    print(event)
    http_method = event['httpMethod']
    if http_method == 'POST':
        return create_device(event)
    elif http_method == 'GET':
        if event.get('queryStringParameters') is None:
            return get_all_devices(event)
        elif "device_id" in event.get('queryStringParameters', {}):
            return get_device(event)
        else:
            return get_all_devices(event)
    elif http_method == 'PUT':
        return update_device(event)
    elif http_method == 'DELETE':
        return delete_device(event)
    else:
        return {
            'statusCode': 500,
            'body': json.dumps("server internal error :unknown error occured ")
        }

def create_device(event):
    payload = json.loads(event['body'])
    device_id = payload['device_id']
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=str(device_id),
        Body=json.dumps(payload)
    )
    return {
        'statusCode': 201,
        'body': json.dumps("Device created Successfully")
    }

def get_device(event):
    device_id = event['queryStringParameters']['device_id']
    try:
        get_device_details = s3.get_object(
            Bucket=BUCKET_NAME,
            Key=str(device_id)
        )
        device_data = get_device_details['Body'].read().decode('utf-8')
        return {
            'statusCode': 200,
            'body': device_data
        }
    except s3.exceptions.NoSuchKey as e:
        print(f"{device_id} doesn't exist")
        return {
            'statusCode': 404,
            'body': json.dumps("Device doesn't exist")
        }

def get_all_devices(event):
    list_devices = s3.list_objects_v2(Bucket=BUCKET_NAME)
    devices = list_devices.get('Contents', [])
    all_devices = []
    for device in devices:
        device_id = device["Key"]
        try:
            get_device_details = s3.get_object(
                Bucket=BUCKET_NAME,
                Key=str(device_id)
            )
            device_data = get_device_details['Body'].read().decode('utf-8')
            all_devices.append(json.loads(device_data))
        except Exception as e:
            print(f"Error fetching with Device with ID {device_id} : {str(e)}")
            continue
    return {
        'statusCode': 200,
        'body': json.dumps(all_devices)
    }

def update_device(event):
       payload = json.loads(event['body'])
       device_id = payload['device_id']
       s3.put_object(
        Bucket=BUCKET_NAME,
        Key=str(device_id),
        Body=json.dumps(payload)
    )
       return {
        'statusCode': 200,
        'body': json.dumps("Device Details updated Successfully")
    }

def delete_device(event):
    device_id = event['queryStringParameters']['device_id']
    s3.delete_object(
        Bucket=BUCKET_NAME,
        Key=device_id
       
    )
    return {
        'statusCode': 200,
        'body': json.dumps(f"Device with ID {device_id}is deleted successfully")
    }
    #pass