FROM public.ecr.aws/lambda/python:3.9

RUN pip install boto3

COPY lambda_function.py ${LAMBDA_TASK_ROOT}

EXPOSE 8080

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]
