# Use Miniconda as the base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /url_classification

# Copy the entire repository into the container
COPY . /url_classification

# Install conda dependencies (if environment.yaml exists)
RUN if [ -f environment.yaml ]; then conda env create -f environment.yaml; fi

# Activate the conda environment
RUN echo "source activate url_classifier" > ~/.bashrc
ENV PATH=/opt/conda/envs/url_classifier/bin:$PATH

# Install pip dependencies (if pip_requirements.txt exists)
RUN if [ -f pip_requirements.txt ]; then conda run -n url_classifier pip install --no-cache-dir -r pip_requirements.txt; fi

# Pre-download the BERT model
RUN conda run -n url_classifier python -c "from transformers import BertTokenizer, BertForMaskedLM; \
    BertTokenizer.from_pretrained('bert-base-uncased'); \
    BertForMaskedLM.from_pretrained('bert-base-uncased')"

# Set default entry to allow interactive mode
ENTRYPOINT ["python", "run_classifier.py"]
CMD ["-v", "http://example.com"]

