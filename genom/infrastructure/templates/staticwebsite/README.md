# Welcome to your CDK Python project!

This is a static website infrastructure project using AWS CDK with Python.

## Architecture

The project follows a clean architecture pattern with centralized configuration management:

### Configuration Management

- **`config.ini`**: Contains all configurable string constants and settings
- **`__init__.py`**: Houses the `ConfigLoader` class with singleton pattern for centralized config management
- **`staticwebsite.py`**: Contains the main CDK Stack class with clean, config-driven implementation

### ConfigLoader Features

- **Singleton Pattern**: Ensures single configuration instance across the application
- **Type-Safe Methods**: Dedicated methods for different configuration sections
- **Error Handling**: Validates config file existence and provides clear error messages
- **Organized Access**: Grouped configuration methods (S3, CloudFront, IAM, etc.)

All string constants and configurable values are externalized to `config.ini` for easy customization without modifying the code.

### Configuration Sections

#### `[DEFAULT]`

- `project_name`: Project identifier used in tagging
- `environment`: Environment identifier (dev, staging, prod)

#### `[S3]`

- `bucket_name`: S3 bucket name for hosting static content
- `default_root_object`: Default file served for root requests
- `error_page_path`: Path to error page for SPA routing

#### `[CloudFront]`

- `comment`: Description for the CloudFront distribution
- `price_class`: CloudFront price class (PRICE_CLASS_100, PRICE_CLASS_200, PRICE_CLASS_ALL)
- `oac_name`: Origin Access Control name
- `oac_description`: Origin Access Control description
- `origin_id`: Origin identifier for CloudFront

#### `[Tags]`

- `bucket_name_tag`: Name tag for S3 bucket
- `cloudfront_name_tag`: Name tag for CloudFront distribution

#### `[IAM]`

- `policy_sid`: Policy statement identifier
- `policy_action`: S3 action allowed by the policy

#### `[Outputs]`

- Various descriptions for CloudFormation outputs

#### `[Timeouts]`

- `error_response_ttl_minutes`: TTL for error responses in minutes

## Configuration Usage

1. Modify `config.ini` with your desired values
2. Deploy using CDK: `cdk deploy`

## Environment-Specific Configurations

To use different configurations for different environments:

1. Create environment-specific config files (e.g., `config-dev.ini`, `config-prod.ini`)
2. Set an environment variable to specify which config to use
3. Modify the code to read the appropriate config file based on the environment

## Security Features

- S3 bucket with public access blocked
- CloudFront with Origin Access Control (OAC) for secure S3 access
- All resources configured for proper destruction during stack deletion

# Original CDK Documentation

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project. The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory. To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation

Enjoy!
