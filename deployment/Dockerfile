FROM python:3.7 AS builder
RUN pip install poetry
COPY . /build
WORKDIR /build
RUN poetry build

FROM python:3.7
COPY --from=builder /build/dist/*.whl /dist/
RUN pip install /dist/*.whl
EXPOSE 8080
CMD ["serve"]
