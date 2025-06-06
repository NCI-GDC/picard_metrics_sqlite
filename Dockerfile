ARG REGISTRY=docker.osdc.io
ARG BASE_CONTAINER_VERSION=2.0.1

FROM ${REGISTRY}/ncigdc/python3.11-builder:${BASE_CONTAINER_VERSION} as builder

COPY ./ /opt

WORKDIR /opt

RUN pip install tox && tox -e build

FROM ${REGISTRY}/ncigdc/python3.11:${BASE_CONTAINER_VERSION}

COPY --from=builder /opt/dist/*.whl /opt/
COPY requirements.txt /opt/

WORKDIR /opt

RUN pip install --no-deps -r requirements.txt \
	&& pip install --no-deps *.whl \
	&& rm -f *.whl requirements.txt

ENTRYPOINT ["picard_metrics_sqlite"]

CMD ["--help"]
