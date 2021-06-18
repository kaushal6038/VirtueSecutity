import boto3
import requests
import json
from redtree_app.models import *
from utils.helpers import get_request_header


class AwsDescriptor:

    def __init__(self, client_asset, region, scan_url=None):
        self.access_token = client_asset.client_aws_access_token
        self.secret_token = client_asset.client_aws_secret_token
        self.asset = client_asset
        self.region = region
        self.client_ec2 = boto3.client(
            'ec2',
            aws_access_key_id=self.access_token,
            aws_secret_access_key=self.secret_token,
            region_name=region
        )
        self.client_s3 = boto3.client(
            's3',
            aws_access_key_id=self.access_token,
            aws_secret_access_key=self.secret_token,
            region_name=region
        )
        self.client_beanstalk = boto3.client(
            'elasticbeanstalk',
            aws_access_key_id=self.access_token,
            aws_secret_access_key=self.secret_token,
            region_name=region
        )
        self.client_rds = boto3.client(
            'rds',
            aws_access_key_id=self.access_token,
            aws_secret_access_key=self.secret_token,
            region_name=region
        )
        self.client_apigateway = boto3.client(
            'apigateway',
            aws_access_key_id=self.access_token,
            aws_secret_access_key=self.secret_token,
            region_name=region
        )
        self.scan_url = scan_url

    def get_ips(self):
        try:
            session = boto3.session.Session(
                aws_access_key_id=self.access_token,
                aws_secret_access_key=self.secret_token,
                region_name=self.region
            )
            ec2 = session.resource('ec2')
            instances = ec2.instances.all()
            public_ips = [each_instance.public_ip_address for each_instance in instances]
            return public_ips
        except Exception as e:
            return []

    def get_buckets(self):
        try:
            buckets = self.client_s3.list_buckets()
            s3_buckets = [bucket['Name'] for bucket in buckets['Buckets']]
            return s3_buckets
        except Exception as e:
            return []

    def get_applications(self):
        try:
            applications = self.client_beanstalk.describe_applications()
            response = [application['ApplicationName'] for application in applications['Applications']]
            return response
        except Exception as e:
            return []

    def get_rds(self):
        try:
            all_stored_rds = AwsRdsEndpoint.objects.all()
            stored_rds = all_stored_rds.filter(asset_link=self.asset)
            all_instances = self.client_rds.describe_db_instances()
            hosts = [(instance.get('Endpoint').get('Address'), instance.get('Endpoint').get('Port')) for instance in
                     all_instances.get('DBInstances')]
            for host, port in hosts:
                if not AwsRdsEndpoint.objects.filter(
                        asset_link=self.asset,
                        host=host,
                        port=int(port),
                        region=self.region
                ).exists():
                    AwsRdsEndpoint.objects.create(
                        asset_link=self.asset,
                        host=host,
                        port=int(port),
                        region=self.region
                    )

            return hosts

        except Exception as e:
            return []

    def get_stages(self, api_id):
        try:
            stage_data = self.client_apigateway.get_stages(
                restApiId=api_id
            )
            if stage_data.get('item'):
                return stage_data['item']
            else:
                return
        except:
            return

    def get_apigateway(self):
        try:
            all_api = []
            all_stored_api = AwsApiGateway.objects.all()
            stored_api = all_stored_api.filter(asset_link=self.asset)
            apisource = self.client_apigateway.get_rest_apis()
            if apisource.get('items'):
                for item in apisource['items']:
                    rest_api_id = item['id']
                    stages = self.get_stages(rest_api_id)
                    for stage in stages:
                        if stage.get('stageName'):
                            url = "https://{0}.execute-api.{1}.amazonaws.com/{2}".format(
                                rest_api_id,
                                self.region,
                                stage['stageName']
                            )
                            all_api.append(url)
                            if not AwsApiGateway.objects.filter(
                                    asset_link=self.asset, api_url=url):
                                AwsApiGateway.objects.create(
                                    asset_link=self.asset,
                                    api_url=url,
                                    region=self.region
                                )
                    for api in stored_api:
                        if api.api_url not in all_api:
                            AwsApiGateway.objects.filter(api_url=api.api_url).delete()
        except Exception as error:
            print
            "no key", error

    def get_permissions(self):
        try:
            buckets = self.get_buckets()
            permissions = {}
            for bucket in buckets:
                responses = requests.post(self.scan_url, json={"bucket_name": bucket, "type": "s3"},
                                          headers={"Content-Type": "application/json"})

                if bucket not in permissions:
                    permissions[bucket] = {"UnAuth": {}, "Auth": {}}

                for permission in responses.text.split('\n'):
                    data = json.loads(permission)

                    permissions[bucket]['UnAuth'] = {"Errors": None, "Issues": None}
                    permissions[bucket]['Auth'] = {"Errors": None, "Issues": None}
                    if "unauthentiated" in data.keys():
                        bucket_obj = data["unauthentiated"][bucket]
                        errors = bucket_obj["errors"]
                        issues = bucket_obj["issues"]
                        if issues:
                            permissions[bucket]['UnAuth']["Issues"] = issues
                        if errors:
                            permissions[bucket]['UnAuth']["Errors"] = errors
                    else:
                        bucket_obj = data["authentiated"][bucket]
                        errors = bucket_obj["errors"]
                        issues = bucket_obj["issues"]
                        if issues:
                            permissions[bucket]['Auth']["Issues"] = issues
                        if errors:
                            permissions[bucket]['Auth']["Errors"] = errors
            return permissions
        except Exception as e:
            print
            e

def cleaned_domain(domain):
    if domain.endswith('.'):
        domain = domain[:-1]
    else:
        domain = domain
    return domain.lower()


def refresh_aws_asset(client_asset):
    if client_asset and client_asset.scan_status and \
            client_asset.scan_state == "Completed":
        client_asset.scan_state = "Running"
        client_asset.save()
        client_conf_obj = ClientConfiguration.objects.first()
        all_ip_addresses = list()
        all_buckets = list()
        all_applications = list()
        all_rds = list()
        access_token = client_asset.client_aws_access_token
        secret_token = client_asset.client_aws_secret_token
        regions = AwsRegion.objects.filter(status=True).values_list(
            'region', flat=True
        )
        try:
            client_route53 = boto3.client(
                'route53',
                aws_access_key_id=access_token,
                aws_secret_access_key=secret_token
            )
        except Exception as e:
            client_asset.scan_state = "Error"
            client_asset.scan_status = True
            client_asset.save()
            print
            'client_route53_Exception::', e
            return False

        try:
            domains = client_route53.list_hosted_zones()
            all_domains = []
            all_stored_domains = AwsDomains.objects.all()
            stored_domains = all_stored_domains.filter(aws_link=client_asset)
            for data in domains.get('HostedZones'):
                resources = client_route53.list_resource_record_sets(
                    HostedZoneId=data.get('Id')
                )
                for domains_data in resources.get('ResourceRecordSets'):
                    if domains_data.get('Type') == "A":
                        domain = cleaned_domain(domains_data.get('Name'))
                        all_domains.append(domain)
                        if not AwsDomains.objects.filter(
                                aws_link=client_asset,
                                domain=domain
                        ).exists():
                            AwsDomains.objects.create(
                                aws_link=client_asset,
                                domain=domain
                            )
            for domain in stored_domains:
                if domain.domain not in all_domains:
                    AwsDomains.objects.filter(aws_link=domain).delete()
        except Exception as e:
            client_asset.scan_state = "Error"
            client_asset.scan_status = True
            client_asset.save()
            print
            'domains_Exception::', e
            return False

        for region in regions:
            aws_descriptor = AwsDescriptor(client_asset, region)
            ip_addresses = aws_descriptor.get_ips()
            all_ip_addresses.extend(ip_addresses)
            buckets = aws_descriptor.get_buckets()
            applications = aws_descriptor.get_applications()
            rds = aws_descriptor.get_rds()
            aws_descriptor.get_apigateway()
            all_buckets.extend(buckets)
            all_applications.extend(applications)
            all_rds.extend(rds)
            # apigateways.extend(api)
        public_ips = set(all_ip_addresses)
        buckets = set(all_buckets)
        applications = set(all_applications)
        hosts = set(all_rds)
        network_obj = None
        if public_ips or buckets:
            try:
                network_obj = Networks.objects.get(
                    network="AWS",
                    network_type="External"
                )
            except Networks.MultipleObjectsReturned:
                network_obj = Networks.objects.filter(
                    network="AWS",
                    network_type="External"
                ).first()
            except Networks.DoesNotExist:
                network_obj = Networks.objects.create(
                    network="AWS",
                    network_type="External"
                )
        if public_ips:
            stored_ips = UserHosts.objects.all()
            aws_link_ips= stored_ips.filter(aws_link=client_asset)
            for stored_ip in aws_link_ips:
                if stored_ip.host not in public_ips:
                    UserHosts.objects.filter(host=stored_ip.host).delete()
            for ip in public_ips:
                if ip and not UserHosts.objects.filter(host=ip).exists():
                    UserHosts.objects.create(
                        host=ip,
                        host_type="ip",
                        network=network_obj,
                        aws_link=client_asset,
                        source="AWS",
                        count=1
                    )
        if buckets:
            stored_buckets = CloudAssetsData.objects.all()
            aws_link_buckets = stored_buckets.filter(aws_link=client_asset)
            for stored_bucket in aws_link_buckets:
                if stored_bucket.bucket not in buckets:
                    CloudAssetsData.objects.filter(bucket=stored_bucket.bucket).delete()
            for bucket in buckets:
                if not CloudAssetsData.objects.filter(
                        bucket=bucket
                ).exists():
                    CloudAssetsData.objects.create(
                        category="S3",
                        network=network_obj,
                        bucket=bucket,
                        aws_link=client_asset,
                        source="AWS"
                    )
        if hosts:
            all_stored_rds = AwsRdsEndpoint.objects.all()
            stored_rds = all_stored_rds.filter(asset_link=client_asset)
            rds_host = [x[0] for x in hosts]
            for rds in stored_rds:
                if rds.host not in rds_host:
                    data = AwsRdsEndpoint.objects.filter(host=rds.host)
                    data.delete()
        if not hosts:
            all_stored_rds = AwsRdsEndpoint.objects.all()
            stored_rds = all_stored_rds.filter(asset_link=client_asset)
            stored_rds.delete()


        client_asset.scan_state = "Completed"
        client_asset.scan_status = True
        client_asset.s3_count = len(buckets)
        client_asset.rds_count = client_asset.rds_endpoints.count()
        client_asset.ec2_count = len(public_ips)
        client_asset.save()