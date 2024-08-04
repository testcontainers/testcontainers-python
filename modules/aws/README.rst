:code:`testcontainers-aws` is a set of AWS containers modules that can be used to create AWS containers.

.. autoclass:: testcontainers.aws.AWSLambdaContainer
.. title:: testcontainers.aws.AWSLambdaContainer

The following environment variables are used by the AWS Lambda container:

+-------------------------------+--------------------------+------------------------------+
| Env Variable                  | Default                  | Notes                        |
+===============================+==========================+==============================+
| ``AWS_DEFAULT_REGION``        | ``us-west-1``            | Fetched from os environment  |
+-------------------------------+--------------------------+------------------------------+
| ``AWS_ACCESS_KEY_ID``         | ``testcontainers-aws``   | Fetched from os environment  |
+-------------------------------+--------------------------+------------------------------+
| ``AWS_SECRET_ACCESS_KEY``     | ``testcontainers-aws``   | Fetched from os environment  |
+-------------------------------+--------------------------+------------------------------+

    Each one of the environment variables is expected to be set in the host machine where the test is running.

Make sure you are using an image based on :code:`public.ecr.aws/lambda/python`

Please checkout https://docs.aws.amazon.com/lambda/latest/dg/python-image.html for more information on how to run AWS Lambda functions locally.
