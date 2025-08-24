# 🚀 AWS ETL Pipeline: S3 → Lambda → Glue → S3

## 📌 Overview  
This project implements a **serverless ETL pipeline** on AWS using **CDK (Python)**.  

- Upload a CSV file into the **Raw S3 bucket**  
- An **S3 Event Notification** triggers a **Lambda function**  
- The Lambda function starts a **Glue Job**  
- Glue reads the CSV, converts it to **Parquet**, and writes to the **Curated S3 bucket**  

✅ Fully automated, event-driven pipeline  
✅ Data stored in **optimized Parquet format**  
✅ Built and deployed with **AWS CDK**  

---

## 🏗️ Architecture

### Mermaid (renders on GitHub)
```mermaid
flowchart LR
    A[Raw S3 Bucket (input/)] -->|PutObject Event| B[Lambda Function]
    B -->|StartJobRun| C[AWS Glue Job]
    C --> D[Curated S3 Bucket (output/)]
PNG Diagram

📂 Project Structure

project/
│── cdk.json
│── app.py
│── cdk/
│   └── pipeline_stack.py       # CDK Infrastructure (S3, Lambda, Roles)
│── lambda/
│   └── s3_file_task/app.py     # Lambda handler: triggers Glue
│── glue/
│   └── etl_job.py              # Glue script: CSV → Parquet
│── sample-data/
│   └── people-100.csv          # Test CSV file
│── assets/
│   └── Architecture.png        # Architecture diagram (static image)
│── README.md
⚙️ Setup Instructions
1. Bootstrap CDK (first-time only)

npx cdk bootstrap
2. Deploy the stack

npx cdk deploy
3. Upload test data

aws s3 cp people-100.csv \
  s3://<RAW_BUCKET_NAME>/input/people-100.csv \
  --region eu-north-1
4. Check output

aws s3 ls s3://<CURATED_BUCKET_NAME>/output/ --region eu-north-1
You should see a .parquet file.

🔑 Key Resources
Raw Bucket: pipelinestack-rawbucket0c3ee094-wnfzms6l97pr

Curated Bucket: pipelinestack-curatedbucket6a59c97e-iyfyhlqhuncl

Lambda Function: TriggerGlueLambda

Glue Job: GlueETLJob

🧪 Testing Flow
Place any CSV into the input/ folder of the Raw bucket.

Lambda will trigger automatically.

Glue will process and save Parquet into output/ of the Curated bucket.

Check logs:


aws logs tail /aws/lambda/<LambdaName> --since 10m --follow --region eu-north-1
📖 Notes
Glue job overwrites output each run (can be changed to append mode).

Buckets are predefined (custom-named in stack).

Uses IAM roles with least-privilege for Lambda + Glue.

✨ Future Improvements
Add Athena table for querying curated Parquet data

Use Step Functions for orchestration

Add data validation layer

👨‍💻 Author
Built by Venkat Mani Shankar