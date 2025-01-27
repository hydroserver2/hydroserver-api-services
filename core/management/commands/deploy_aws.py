import os
from django.core.management.base import BaseCommand
from pydantic import BaseModel, Field, DirectoryPath, ConfigDict
from typing import Literal


class DeploySettings(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    instance: Literal['dev', 'beta'] = Field(
        ..., alias='--instance',
        help='Specify the HydroServer instance you want to deploy to. Options are ["dev", "beta"]'
    )
    frontend: DirectoryPath = Field(
        ..., alias='--frontend',
        help='Enter the path to the frontend repository you want to bundle with this deployment.'
    )
    backend: DirectoryPath = Field(
        ..., alias='--backend',
        help='Enter the path to the backend repository you want to bundle with this deployment.'
    )
    eb_version: str = Field(
        ..., alias='--eb-version',
        help='Enter an AWS EB application version for this deployment.'
    )
    cloudfront_id: str = Field(
        ..., alias='--cloudfront-id',
        help='Enter the CloudFront distribution ID for this deployment.'
    )


class Command(BaseCommand):

    def add_arguments(self, parser):
        for field, meta in DeploySettings.__fields__.items():
            parser.add_argument(meta.alias, type=str, help=meta.field_info.extra.get('help'))

    def handle(self, *args, **options):
        deploy_settings = DeploySettings(**options)

        ignored_files = [
            '*__pycache__*', '*.env*', '*pytest*', '*.sqlite*', '*.git/*', '*staticfiles*', '*elasticbeanstalk*',
            '*.DS_Store*', '*.idea*', '*deploy_package.zip*'
        ]

        os.system(
            f'cd {deploy_settings.backend}; zip -r deploy_package.zip ./ ' +
            ' '.join(['-x "' + i + '"' for i in ignored_files])
        )

        os.system(
            f'aws s3 cp {os.path.join(deploy_settings.backend, "deploy_package.zip")} ' +
            f's3://hydroserver/deployment/{deploy_settings.instance}/' +
            f'deploy_package_{deploy_settings.eb_version}.zip'
        )

        os.system(
            f'aws elasticbeanstalk create-application-version ' +
            f'--application-name hydroserver-{deploy_settings.instance} ' +
            f'--source-bundle S3Bucket="hydroserver",' +
            f'S3Key="deployment/{deploy_settings.instance}/deploy_package_{deploy_settings.eb_version}.zip" ' +
            f'--version-label "{deploy_settings.eb_version}" ' +
            f'--description "manual-deployment-{deploy_settings.eb_version}"'
        )

        os.system(
            f'aws elasticbeanstalk update-environment --environment-name hydroserver-{deploy_settings.instance}-env ' +
            f'--version-label "{deploy_settings.eb_version}"'
        )

        os.system(
            f'aws s3 sync {deploy_settings.frontend} s3://hydroserver-{deploy_settings.instance}-web/ --delete'
        )

        os.system(
            f'aws cloudfront create-invalidation --distribution-id {deploy_settings.cloudfront_id } --paths "/*"'
        )
