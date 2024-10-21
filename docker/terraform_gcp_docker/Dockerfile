FROM hashicorp/terraform:latest

WORKDIR /terraform

COPY . .

RUN  terraform init

ENTRYPOINT ["terraform"]

CMD ["apply", "-auto-approve"]