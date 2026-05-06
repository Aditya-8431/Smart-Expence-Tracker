"""
train_model.py - Improved training data with better keyword coverage
"""

import os
import joblib
import numpy  as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble                 import RandomForestClassifier
from sklearn.model_selection          import train_test_split
from sklearn.metrics                  import accuracy_score, classification_report

EXPENSE_DATA = [
    # Food
    ("paid for lunch at restaurant",        "Food"),
    ("pizza delivery order",                "Food"),
    ("bought groceries from supermarket",   "Food"),
    ("coffee at cafe",                      "Food"),
    ("cold coffee",                         "Food"),
    ("hot coffee",                          "Food"),
    ("cold coffee from cafe",               "Food"),
    ("cold coffee starbucks",               "Food"),
    ("dinner with family",                  "Food"),
    ("breakfast at hotel",                  "Food"),
    ("ordered biryani from zomato",         "Food"),
    ("swiggy food order",                   "Food"),
    ("burger and fries",                    "Food"),
    ("milk eggs bread from kirana",         "Food"),
    ("ice cream parlour",                   "Food"),
    ("snacks and chips",                    "Food"),
    ("tea and samosa",                      "Food"),
    ("chinese food takeaway",               "Food"),
    ("restaurant bill",                     "Food"),
    ("dominos pizza",                       "Food"),
    ("grocery shopping bigbasket",          "Food"),
    ("vegetables and fruits market",        "Food"),
    ("birthday cake bakery",                "Food"),
    ("office canteen lunch",                "Food"),
    ("paid for food",                       "Food"),
    ("paid for dinner",                     "Food"),
    ("paid for breakfast",                  "Food"),
    ("paid for lunch",                      "Food"),
    ("paid for coffee",                     "Food"),
    ("paid for tea",                        "Food"),
    ("paid for pizza",                      "Food"),
    ("paid for biryani",                    "Food"),
    ("food order",                          "Food"),
    ("meal",                                "Food"),
    ("juice",                               "Food"),
    ("smoothie",                            "Food"),
    ("chai",                                "Food"),
    ("lassi",                               "Food"),
    ("dosa",                                "Food"),
    ("idli",                                "Food"),
    ("paratha",                             "Food"),
    ("noodles",                             "Food"),
    ("maggi",                               "Food"),
    ("sandwich",                            "Food"),
    ("fruit juice",                         "Food"),
    ("70 for cold coffee",                  "Food"),
    ("paid for cold coffee",                "Food"),
    ("coffee",                               "Food"),
    ("restaurant",                           "Food"),
    ("grocery",                              "Food"),
    ("supermarket",                         "Food"),
    ("sabji",                                "Food"),
    ("vegetables",                          "Food"),
    ("fruits",                                "Food"),
    ("clod drink",                          "Food"),
    ("snacks",                               "Food"),
    ("food",                                 "Food"),
    ("meal",                                 "Food"),
     ("dinner",                               "Food"),
     ("breakfast",                            "Food"),
     ("lunch",                                "Food"),
     ("tea",                                  "Food"),
    ("pizza",                                "Food"),
    ("biryani",                              "Food"),
     ("coffee",                               "Food"),


    # Transport
    ("uber cab ride",                       "Transport"),
    ("ola auto ride",                       "Transport"),
    ("paid for auto",                       "Transport"),
    ("paid 20 for auto",                    "Transport"),
    ("auto rickshaw fare",                  "Transport"),
    ("auto ride",                           "Transport"),
    ("auto fare",                           "Transport"),
    ("took auto",                           "Transport"),
    ("paid auto",                           "Transport"),
    ("petrol filling station",              "Transport"),
    ("metro train ticket",                  "Transport"),
    ("bus pass monthly",                    "Transport"),
    ("rapido bike taxi",                    "Transport"),
    ("fuel diesel car",                     "Transport"),
    ("parking charges mall",                "Transport"),
    ("toll plaza highway",                  "Transport"),
    ("train ticket irctc",                  "Transport"),
    ("airport cab",                         "Transport"),
    ("local bus fare",                      "Transport"),
    ("vehicle service charges",             "Transport"),
    ("car washing",                         "Transport"),
    ("bike petrol",                         "Transport"),
    ("redbus ticket booking",               "Transport"),
    ("monthly metro card recharge",         "Transport"),
    ("cab fare",                            "Transport"),
    ("taxi fare",                           "Transport"),
    ("bus fare",                            "Transport"),
    ("rickshaw",                            "Transport"),
    ("e rickshaw",                          "Transport"),
    ("bike ride",                           "Transport"),
    ("petrol",                              "Transport"),
    ("diesel",                              "Transport"),
    ("uber",                                "Transport"),
    ("ola",                                 "Transport"),
    ("rapido",                              "Transport"),
    ("metro",                               "Transport"),
    ("bus ticket",                          "Transport"),
    ("cab booking",                         "Transport"),
    ("travel by auto",                      "Transport"),
    ("travel by bus",                       "Transport"),
    ("travel by metro",                     "Transport"),
    ("auto",                                "Transport"),
    ("bus",                                 "Transport"),
    ("train",                               "Transport"),
    ("flight",                              "Transport"),
    ("transport",                            "Transport"),
    ("ride",                                 "Transport"),
    ("fare",                                 "Transport"),
    ("petrol",                              "Transport"),
    ("diesel",                              "Transport"),
    ("fuel",                                "Transport"),
    ("parking",                              "Transport"),
    ("toll",                                 "Transport"),
    ("car ",                                 "Transport"),
    ("washing",                              "Transport"),


    # Shopping
    ("amazon online shopping",              "Shopping"),
    ("flipkart order placed",               "Shopping"),
    ("clothes from myntra",                 "Shopping"),
    ("shoes purchased",                     "Shopping"),
    ("mobile accessories",                  "Shopping"),
    ("new shirt from mall",                 "Shopping"),
    ("jeans and tshirt",                    "Shopping"),
    ("meesho order delivered",              "Shopping"),
    ("earphones headphones bought",         "Shopping"),
    ("watch purchase",                      "Shopping"),
    ("bag backpack new",                    "Shopping"),
    ("sunglasses spectacles",               "Shopping"),
    ("home decor items",                    "Shopping"),
    ("kitchen utensils vessels",            "Shopping"),
    ("stationery pens notebooks",           "Shopping"),
    ("ajio clothing order",                 "Shopping"),
    ("nykaa cosmetics purchase",            "Shopping"),
    ("furniture shopping",                  "Shopping"),
    ("bought clothes",                      "Shopping"),
    ("bought shoes",                        "Shopping"),
    ("bought shirt",                        "Shopping"),
    ("online order",                        "Shopping"),
    ("amazon order",                        "Shopping"),
    ("flipkart",                            "Shopping"),
    ("myntra",                              "Shopping"),
    ("meesho",                              "Shopping"),
    ("ajio",                                "Shopping"),
    ("nykaa",                               "Shopping"),
    ("furniture",                           "Shopping"),
    ("clothes",                             "Shopping"),
    ("shoes",                               "Shopping"),
    ("mobile accessories",                  "Shopping"),
    ("watch",                               "Shopping"),
    ("bag",                                 "Shopping"),
    ("sunglasses",                          "Shopping"),
    ("home decor",                          "Shopping"),
    ("kitchen utensils",                    "Shopping"),
    ("stationery",                          "Shopping"),
    ("shopping",                            "Shopping"),
     ("clothing",                            "Shopping"),
     ("footwear",                            "Shopping"),
     ("accessories",                         "Shopping"),
     ("furniture",                            "Shopping"),
     ("decor",                                "Shopping"),  
     
     

    # Entertainment
    ("movie ticket pvr inox",               "Entertainment"),
    ("netflix subscription",                "Entertainment"),
    ("spotify premium music",               "Entertainment"),
    ("amazon prime video",                  "Entertainment"),
    ("youtube premium",                     "Entertainment"),
    ("gaming top up pubg",                  "Entertainment"),
    ("concert event ticket",                "Entertainment"),
    ("amusement park entry",                "Entertainment"),
    ("hotstar subscription",                "Entertainment"),
    ("steam game purchase",                 "Entertainment"),
    ("disney plus subscription",            "Entertainment"),
    ("cricket match ticket",                "Entertainment"),
    ("movie",                               "Entertainment"),
    ("netflix",                             "Entertainment"),
    ("prime video",                         "Entertainment"),
    ("hotstar",                             "Entertainment"),
    ("game",                                "Entertainment"),
    ("Entertainment",                          "Entertainment"),


    # Health
    ("pharmacy medicine purchase",          "Health"),
    ("doctor consultation fee",             "Health"),
    ("gym membership monthly",              "Health"),
    ("hospital bill payment",               "Health"),
    ("health checkup diagnostic",           "Health"),
    ("yoga class fees",                     "Health"),
    ("dental clinic treatment",             "Health"),
    ("vitamins supplements purchase",       "Health"),
    ("blood test lab",                      "Health"),
    ("protein powder supplement",           "Health"),
    ("medicine",                            "Health"),
    ("doctor",                              "Health"),
    ("hospital",                            "Health"),
    ("pharmacy",                            "Health"),
    ("gym",                                 "Health"),
    ("tablets",                             "Health"),
    ("medicine purchase",                    "Health"),
    ("consultation fee",                    "Health"),
    ("health checkup",                      "Health"),
    ("yoga class",                          "Health"),
    ("dental treatment",                    "Health"), 
     ("medicine ",                          "Health"),


    # Utilities
    ("electricity bill payment",            "Utilities"),
    ("water bill monthly",                  "Utilities"),
    ("internet broadband recharge",         "Utilities"),
    ("mobile recharge prepaid",             "Utilities"),
    ("gas cylinder lpg booking",            "Utilities"),
    ("airtel broadband bill",               "Utilities"),
    ("jio recharge plan",                   "Utilities"),
    ("dish tv dth recharge",                "Utilities"),
    ("house rent payment",                  "Utilities"),
    ("maintenance society charges",         "Utilities"),
    ("postpaid mobile bill",                "Utilities"),
    ("wifi monthly payment",                "Utilities"),
    ("electricity bill",                    "Utilities"),
    ("phone bill",                          "Utilities"),
    ("recharge",                            "Utilities"),
    ("rent",                                "Utilities"),
    ("gas bill",                            "Utilities"),
    ("lpg booking",                          "Utilities"),
    ("broadband bill",                      "Utilities"),
    ("dth recharge",                        "Utilities"),
    ("society maintenance",                 "Utilities"),
    ("house rent",                          "Utilities"),
    ("apartment rent",                      "Utilities"),
    ("mobile bill",                         "Utilities"),
    ("internet bill",                       "Utilities"),
    ("wifi bill",                           "Utilities"),
    ("utilities",                            "Utilities"),
    ("electricity",                          "Utilities"),
    ("water",                               "Utilities"),
    ("internet",                            "Utilities"),
    ("gas",                                 "Utilities"),
    ("rent",                                "Utilities"),
    ("maintenance",                          "Utilities"),
    ("broadband",                          "Utilities"),
    ("dth",                                "Utilities"),
    ("mobile",                              "Utilities"),
    ("bartan",                              "Utilities"),
    ("utensils",                            "Utilities"),
    ("household items",                    "Utilities"),

    

    # Travel
    ("flight ticket booking",               "Travel"),
    ("hotel booking oyo",                   "Travel"),
    ("airbnb accommodation",                "Travel"),
    ("goibibo flight",                      "Travel"),
    ("make my trip hotel",                  "Travel"),
    ("holiday package tour",                "Travel"),
    ("visa application fee",                "Travel"),
    ("resort stay weekend",                 "Travel"),
    ("hotel",                               "Travel"),
    ("oyo",                                 "Travel"),
    ("holiday",                             "Travel"),
    ("tour",                                "Travel"),
    ("trip expenses",                       "Travel"),

    # Education
    ("udemy course purchase",               "Education"),
    ("coursera subscription",               "Education"),
    ("college tuition fee",                 "Education"),
    ("school fees payment",                 "Education"),
    ("book textbook purchase",              "Education"),
    ("coaching classes fees",               "Education"),
    ("online certification exam",           "Education"),
    ("unacademy subscription",              "Education"),
    ("byju course enrollment",              "Education"),
    ("course",                              "Education"),
    ("tuition",                             "Education"),
    ("class fees",                          "Education"),
    ("exam fees",                           "Education"),
    ("copy and pen purchase",                 "Education"),
    ("copy",                               "Education"),
    ("pen",                                "Education"),
    ("notebook",                            "Education"),
    ("education",                            "Education"),
    ("book",                                "Education"),

]


def preprocess(text):
    return text.lower().strip()


def train():
    print("=" * 55)
    print("  Smart Expense Tracker — Model Training")
    print("=" * 55)

    df = pd.DataFrame(EXPENSE_DATA, columns=["description", "category"])
    df["description"] = df["description"].apply(preprocess)
    labels = sorted(df["category"].unique().tolist())

    print(f"\n[1/5] Dataset: {len(df)} samples | {len(labels)} categories")

    X_train, X_test, y_train, y_test = train_test_split(
        df["description"], df["category"],
        test_size=0.2, random_state=42, stratify=df["category"]
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)

    clf = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    clf.fit(X_train_vec, y_train)

    y_pred   = clf.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n[5/5] Accuracy: {accuracy * 100:.1f}%\n")
    print(classification_report(y_test, y_pred))

    bundle = {"vectorizer": vectorizer, "classifier": clf, "labels": labels}
    save_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    joblib.dump(bundle, save_path)
    print(f"✅  Model saved → {save_path}")


if __name__ == "__main__":
    train()