# Problem Statement

Late deliveries are the biggest driver of bad reviews in e-commerce.
ShipSense estimates the risk that an order will arrive after its promised
date, so operations staff can act early. It also summarizes what customers
say in their reviews.

## Users
- Operations analyst at an online marketplace

## Success metrics
- Delay model beats the baseline on PR-AUC (baseline is about the late rate, ~8%)
- Delay model catches at least 60% of late orders (recall) at a stated precision
- Prediction API responds in under 300 ms locally

## Out of scope
- Real-time carrier tracking
- User accounts and login

## Data
Olist Brazilian E-commerce dataset (Kaggle), about 100k orders, 2016 to 2018.
