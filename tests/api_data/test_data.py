# flake8: noqa
assessor_task_list_test_metadata = metadata = {
    "criterias": [
        {
            "name": "Strategic case",
            "sub_criterias": [
                {
                    "id": "benefits",
                    "name": "Benefits",
                    "score": 5,
                    "status": "COMPLETED",
                    "theme_count": 2,
                },
            ],
            "total_criteria_score": 12,
            "total_criteria_score_possible": 15,
            "weighting": 0.3,
        },
        {
            "name": "Management case",
            "sub_criterias": [
                {
                    "id": "funding_breakdown",
                    "name": "Funding breakdown",
                    "score": 5,
                    "status": "COMPLETED",
                    "theme_count": 1,
                },
            ],
            "total_criteria_score": 16,
            "total_criteria_score_possible": 20,
            "weighting": 0.3,
        },
        {
            "name": "Potential to deliver community benefit",
            "sub_criterias": [
                {
                    "id": "community-benefits",
                    "name": "How the community benefits\t",
                    "score": 5,
                    "status": "COMPLETED",
                    "theme_count": 1,
                },
            ],
            "total_criteria_score": 10,
            "total_criteria_score_possible": 10,
            "weighting": 0.3,
        },
        {
            "name": "Added value of the community asset",
            "sub_criterias": [
                {
                    "id": "value-to-the-community",
                    "name": "Value to the community",
                    "score": 2,
                    "status": "COMPLETED",
                    "theme_count": 1,
                }
            ],
            "total_criteria_score": 2,
            "total_criteria_score_possible": 5,
            "weighting": 0.1,
        },
    ],
    "date_submitted": "2022-10-27T08:32:13.383999",
    "fund_id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
    "funding_amount_requested": 4600.0,
    "project_name": "Restore the humble skatepark in Brighton",
    "sections": [
        {
            "name": "Unscored",
            "sub_criterias": [
                {"id": "org_info", "name": "Organisation information"},
                {"id": "applicant_info", "name": "Applicant information"},
                {"id": "project_info", "name": "Project information"},
                {"id": "asset_info", "name": "Asset information"},
                {"id": "business_plan", "name": "Business plan"},
            ],
        },
        {
            "name": "Declarations",
            "sub_criterias": [
                {"id": "declarations", "name": "Declarations"},
                {
                    "id": "subsidy_control_and_state_aid",
                    "name": "Subsidy control and state aid",
                },
            ],
        },
    ],
    "short_id": "COF-R2W2-LREIBX",
    "workflow_status": "COMPLETED",
}

single_application_json_blob = {
    "account_id": "cbf981cf-5238-4d3e-84e9-b9c183789a91",
    "date_submitted": "2022-10-27T08:32:13.383999",
    "forms": [
        {
            "name": "feasibility",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "lots of surveys",
                            "key": "ieRCkI",
                            "title": (
                                "Tell us about the feasibility studies you"
                                " have carried out for your project"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": False,
                            "key": "aAeszH",
                            "title": (
                                "Do you need to do any further feasibility"
                                " work?"
                            ),
                            "type": "list",
                        },
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "risk",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "sample1.doc",
                            "key": "ozgwXq",
                            "title": "Risks to your project (document upload)",
                            "type": "file",
                        }
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "community-use",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": ["support-local-community"],
                            "key": "CDwTrG",
                            "title": (
                                "What policy aims will your project deliver"
                                " against?"
                            ),
                            "type": "list",
                        },
                        {
                            "answer": "Test",
                            "key": "kxgWTy",
                            "title": (
                                "Who in the community uses the asset, or has"
                                " used it in the past, and who benefits"
                                " from it?"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "GNhrIs",
                            "title": (
                                "Tell us how losing the asset would affect, or"
                                " has already affected, people in the"
                                " community"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "qsZLjZ",
                            "title": (
                                "Why will the asset be lost without community"
                                " intervention?"
                            ),
                            "type": "text",
                        },
                    ],
                    "question": "Strategic case",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "environmental-sustainability",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "Test",
                            "key": "CvVZJv",
                            "title": (
                                "Tell us how you have considered the"
                                " environmental sustainability of your project"
                            ),
                            "type": "text",
                        }
                    ],
                    "question": "Strategic case",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "local-support",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "KqoaJL",
                            "title": (
                                "Are you confident there is local support for"
                                " your project?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "Strategic case",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "project-qualification",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "HvxXPI",
                            "title": (
                                "Does your project meet the definition of a"
                                " subsidy?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "Subsidy control and state aid",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "skills-and-resources",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "CBIWnt",
                            "title": (
                                "Do you have experience of managing a"
                                " community asset?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "vKnMPG",
                            "title": (
                                "Do you have any plans to recruit people to"
                                " help you manage the asset?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                },
            ],
            "status": "COMPLETED",
        },
        {
            "name": "upload-business-plan",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "awskey123123123123123/sample1.doc",
                            "key": "rFXeZo",
                            "title": "Upload business plan",
                            "type": "file",
                        }
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "upload-no-plan",
            "questions": [
                {
                    "fields": [
                        {
                            # Intentionally missing "answer" key for testing
                            "key": "rFXeZo",
                            "title": "Upload NO plan",
                            "type": "file",
                        }
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "project-information",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "gScdbf",
                            "title": (
                                "Have you been given funding through the"
                                " Community Ownership Fund before?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": (
                                "Restore the beautiful museum in Bristol"
                            ),
                            "key": "KAgrBz",
                            "title": "Project name",
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "wudRxx",
                            "title": (
                                "Tell us how the asset is currently being"
                                " used, or how it has been used before, and"
                                " why it's important to the community"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "TlGjXb",
                            "title": (
                                "Explain why the asset is at risk of being"
                                " lost to the community, or why it has already"
                                " been lost"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "GCjCse",
                            "title": (
                                "Give a brief summary of your project,"
                                " including what you hope to achieve"
                            ),
                            "type": "text",
                        },
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": (
                                "Test Address, null, Test Town Or City, null,"
                                " QQ12QQ"
                            ),
                            "key": "yEmHpp",
                            "title": "Address of the community asset",
                            "type": "text",
                        },
                        {
                            "answer": "Constituency",
                            "key": "iTeLGU",
                            "title": "In which constituency is your asset?",
                            "type": "text",
                        },
                        {
                            "answer": "Local Council",
                            "key": "MGRlEi",
                            "title": (
                                "In which local council area is your asset?"
                            ),
                            "type": "text",
                        },
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
            ],
            "status": "COMPLETED",
        },
        {
            "name": "organisation-information",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "ANON-###-###-###",
                            "key": "WWWWxy",
                            "title": "Your unique tracker number",
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "YdtlQZ",
                            "title": "Organisation name",
                            "type": "text",
                        },
                        {
                            "answer": False,
                            "key": "iBCGxY",
                            "title": (
                                "Does your organisation use any other names?"
                            ),
                            "type": "list",
                        },
                    ],
                    "question": "About your organisation",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": "Test",
                            "key": "emVGxS",
                            "title": (
                                "What is your organisation's main purpose?"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "btTtIb",
                            "title": (
                                "Tell us about your organisation's main"
                                " activities"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "",
                            "key": "SkocDi",
                            "title": (
                                "Tell us about your organisation's main"
                                " activities - Activity 2 "
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "",
                            "key": "CNeeiC",
                            "title": (
                                "Tell us about your organisation's main"
                                " activities - Activity 3 "
                            ),
                            "type": "text",
                        },
                        {
                            "answer": False,
                            "key": "BBlCko",
                            "title": (
                                "Have you delivered projects like this before?"
                            ),
                            "type": "list",
                        },
                    ],
                    "question": "About your organisation",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": "CIO",
                            "key": "lajFtB",
                            "title": "Type of organisation",
                            "type": "list",
                        }
                    ],
                    "question": "About your organisation",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": "Test",
                            "key": "aHIGbK",
                            "title": "Charity number ",
                            "type": "text",
                        }
                    ],
                    "question": "About your organisation",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "DwfHtk",
                            "title": (
                                "Is your organisation a trading subsidiary of"
                                " a parent company?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "About your organisation",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": (
                                "Test Address, null, Test Town Or City, null,"
                                " QQ12QQ"
                            ),
                            "key": "ZQolYb",
                            "title": "Organisation address",
                            "type": "text",
                        },
                        {
                            "answer": False,
                            "key": "zsoLdf",
                            "title": (
                                "Is your correspondence address different to"
                                " the organisation address?"
                            ),
                            "type": "list",
                        },
                        {
                            "answer": "https://twitter.com/luhc",
                            "key": "FhbaEy",
                            "title": "Website and social media ",
                            "type": "text",
                        },
                        {
                            "answer": "",
                            "key": "FcdKlB",
                            "title": (
                                "Website and social media - Link or username 2"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "",
                            "key": "BzxgDA",
                            "title": (
                                "Website and social media - Link or username 3"
                            ),
                            "type": "text",
                        },
                    ],
                    "question": "About your organisation",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "hnLurH",
                            "title": (
                                "Is your application a joint bid in"
                                " partnership with other organisations?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "About your organisation",
                    "status": "COMPLETED",
                },
            ],
            "status": "COMPLETED",
        },
        {
            "name": "applicant-information",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "Test Name",
                            "key": "ZBjDTn",
                            "title": "Name of lead contact",
                            "type": "text",
                        },
                        {
                            "answer": "testemailfundingservice@"
                            + "testemailfundingservice.com",
                            "key": "LZBrEj",
                            "title": "Lead contact email address",
                            "type": "text",
                        },
                        {
                            "answer": "0000000000",
                            "key": "lRfhGB",
                            "title": "Lead contact telephone number",
                            "type": "text",
                        },
                    ],
                    "question": "About your organisation",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "asset-information",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "museum",
                            "key": "yaQoxU",
                            "title": "Asset type",
                            "type": "list",
                        }
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": "buy-the-asset",
                            "key": "VWkLlk",
                            "title": (
                                "What do you intend to do with the asset?"
                            ),
                            "type": "list",
                        },
                        {
                            "answer": False,
                            "key": "IRfSZp",
                            "title": (
                                "Do you know who currently owns your asset?"
                            ),
                            "type": "list",
                        },
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": "Current Owner",
                            "key": "FtDJfK",
                            "title": "Describe the current ownership status",
                            "type": "text",
                        }
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "gkulUE",
                            "title": (
                                "Have you already completed the purchase or"
                                " lease?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": "Test",
                            "key": "nvMmGE",
                            "title": (
                                "Describe the expected sale process, or the"
                                " proposed terms of your lease if you are"
                                " renting the asset"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "2022-12-01",
                            "key": "ghzLRv",
                            "title": "Expected date of sale or lease",
                            "type": "date",
                        },
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "Wyesgy",
                            "title": "Is your asset currently publicly owned?",
                            "type": "list",
                        }
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "hvzzWB",
                            "title": (
                                "Is this a registered Asset of Community Value"
                                " (ACV)?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "VwxiGn",
                            "title": (
                                "Is the asset listed for disposal, or part of"
                                " a Community Asset Transfer?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "About your project ",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": ["for-sale-or-listed-for-disposal"],
                            "key": "UDTxqC",
                            "title": "Why is the asset at risk of closure?",
                            "type": "list",
                        }
                    ],
                    "question": "About your project",
                    "status": "COMPLETED",
                },
            ],
            "status": "COMPLETED",
        },
        {
            "name": "community-engagement",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": (
                                "Tell us how you have engaged with the"
                                " community about your intention to take"
                                " ownership of the asset"
                            ),
                            "key": "HJBgvw",
                            "title": (
                                "Tell us how you have engaged with the"
                                " community about your intention to take"
                                " ownership of the asset, and explain how this"
                                " has shaped your project plans"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": False,
                            "key": "JCACTy",
                            "title": (
                                "Have you done any fundraising in the"
                                " community?"
                            ),
                            "type": "list",
                        },
                    ],
                    "question": "Strategic case",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": (
                                "Tell us how your project supports any wider"
                                " local plans"
                            ),
                            "key": "NZKHOp",
                            "title": (
                                "Tell us how your project supports any wider"
                                " local plans"
                            ),
                            "type": "text",
                        }
                    ],
                    "question": "Strategic case",
                    "status": "COMPLETED",
                },
            ],
            "status": "COMPLETED",
        },
        {
            "name": "funding-required",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "2300",
                            "key": "JzWvhj",
                            "title": "Capital funding",
                            "type": "text",
                        },
                        {
                            "answer": "2300",
                            "key": "jLIgoi",
                            "title": "Revenue funding (optional)",
                            "type": "text",
                        },
                    ],
                    "question": "Management case ",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": ["Capital Funding : \u00a32300"],
                            "key": "MultiInputField",
                            "title": "Capital costs",
                            "type": "text",
                        }
                    ],
                    "question": "Management case ",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "NWTKzQ",
                            "title": (
                                "Are you applying for revenue funding from the"
                                " Community Ownership Fund? (optional)"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "Management case ",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "DIZZOC",
                            "title": "Have you secured any match funding yet?",
                            "type": "list",
                        }
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": False,
                            "key": "RvbwSX",
                            "title": (
                                "Do you have any match funding identified but"
                                " not yet secured?"
                            ),
                            "type": "list",
                        }
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": "2300",
                            "key": "fnIdkJ",
                            "title": "Asset value",
                            "type": "text",
                        }
                    ],
                    "question": "Management case ",
                    "status": "COMPLETED",
                },
            ],
            "status": "COMPLETED",
        },
        {
            "name": "community-benefits",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": ["community-pride"],
                            "key": "QjJtbs",
                            "title": (
                                "What community benefits do you expect to"
                                " deliver with this project? "
                            ),
                            "type": "list",
                        },
                        {
                            "answer": "Test",
                            "key": "gDTsgG",
                            "title": (
                                "Tell us about these benefits in detail, and"
                                " explain how you'll measure the benefits"
                                " it'll bring for the community"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "kYjJFy",
                            "title": (
                                "Explain how you plan to sustain, and"
                                " potentially expand, these benefits over time"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "UbjYqE",
                            "title": (
                                "Tell us how you'll make sure the whole"
                                " community benefits from the asset"
                            ),
                            "type": "text",
                        },
                    ],
                    "question": "Potential to deliver community benefits",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "inclusiveness-and-integration",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "Test",
                            "key": "SrtVAs",
                            "title": (
                                "Describe the planned activities or services"
                                " that will take place at the asset"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "YbfbSC",
                            "title": (
                                "Describe anything that might prevent people"
                                " from using the asset or participating in its"
                                " running"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "KuhSWw",
                            "title": (
                                "Tell us how you'll make your project"
                                " accessible and inclusive to everyone in the"
                                " community"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "bkJsiO",
                            "title": (
                                "Describe how the project will bring people"
                                " together from all over the community"
                            ),
                            "type": "text",
                        },
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "project-costs",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "Test",
                            "key": "WDDkVB",
                            "title": (
                                "Summarise your cash flow for the running of"
                                " the asset"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": False,
                            "key": "oaIntA",
                            "title": (
                                "If successful, will you use your funding in"
                                " the next 12 months?"
                            ),
                            "type": "list",
                        },
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": ["Income Test : \u00a32300"],
                            "key": "MultiInputField",
                            "title": "Sources of income",
                            "type": "text",
                        }
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                },
                {
                    "fields": [
                        {
                            "answer": ["Running Cost Test : \u00a32300"],
                            "key": "MultiInputField-2",
                            "title": "Running costs",
                            "type": "text",
                        }
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                },
            ],
            "status": "COMPLETED",
        },
        {
            "name": "community-representation",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "Test",
                            "key": "JnvsPq",
                            "title": "List the members of your board",
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "yMCivI",
                            "title": (
                                "Tell us about your governance and membership"
                                " structures"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "NUZOvS",
                            "title": (
                                "Explain how you'll consider the views of the"
                                " community in the running of the asset"
                            ),
                            "type": "text",
                        },
                    ],
                    "question": "Management case",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "value-to-the-community",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": "Test",
                            "key": "oOPUXI",
                            "title": (
                                "Tell us about your local community as a whole"
                            ),
                            "type": "text",
                        },
                        {
                            "answer": "Test",
                            "key": "NKOmNL",
                            "title": (
                                "Describe any specific challenges your"
                                " community faces, and how the asset will"
                                " address these"
                            ),
                            "type": "text",
                        },
                    ],
                    "question": "Added value to the community",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
        {
            "name": "declarations",
            "questions": [
                {
                    "fields": [
                        {
                            "answer": True,
                            "key": "LlvhYl",
                            "title": (
                                "Confirm you have considered subsidy control"
                                " and state aid implications for your project,"
                                " and the information you have given us is"
                                " correct"
                            ),
                            "type": "list",
                        },
                        {
                            "answer": False,
                            "key": "wJrJWY",
                            "title": (
                                "Confirm you have considered people with"
                                " protected characteristics throughout the"
                                " planning of your project"
                            ),
                            "type": "list",
                        },
                        {
                            "answer": True,
                            "key": "COiwQr",
                            "title": (
                                "Confirm you have considered sustainability"
                                " and the environment throughout the planning"
                                " of your project, including compliance with"
                                " the government's Net Zero ambitions"
                            ),
                            "type": "list",
                        },
                        {
                            "answer": False,
                            "key": "bRPzWU",
                            "title": (
                                "Confirm you have a bank account set up and"
                                " associated with the organisation you are"
                                " applying on behalf of"
                            ),
                            "type": "list",
                        },
                    ],
                    "question": "Declarations",
                    "status": "COMPLETED",
                }
            ],
            "status": "COMPLETED",
        },
    ],
    "fund_id": "1cf77fc2-036f-4f70-888f-2341b43f57ae",
    "id": "d87e8dcd-7a51-4b27-8c53-d6c466986b66",
    "last_edited": "2022-10-27T08:32:11.843201",
    "project_name": "Restore the beautiful museum in Bristol",
    "reference": "COF-R2W2-LXPUSJ",
    "round_id": "b093a740-da04-4d6f-9d1e-1e38fd062beb",
    "round_name": "Round 2 Window 2",
    "started_at": "2022-10-27T08:28:55.699864",
    "status": "SUBMITTED",
    "location_json_blob": {
        "error": False,
        "county": "test-county",
        "region": "England",
        "country": "England",
        "postcode": "QQ12QQ",
        "constituency": "test-constituency",
    },
}

test_application_answers = {
    "feasibility": {
        "Tell us about the feasibility studies you have carried out for your project": (
            "lots of surveys"
        ),
        "Do you need to do any further feasibility work?": False,
    },
    "risk": {"Risks to your project (document upload)": "sample1.doc"},
    "community-use": {
        "What policy aims will your project deliver against?": [
            "support-local-community"
        ],
        "Who in the community uses the asset, or has used it in the past, and who benefits from it?": (
            "Test"
        ),
        "Tell us how losing the asset would affect, or has already affected, people in the community": (
            "Test"
        ),
        "Why will the asset be lost without community intervention?": "Test",
    },
    "environmental-sustainability": {
        "Tell us how you have considered the environmental sustainability of your project": (
            "Test"
        )
    },
    "local-support": {
        "Are you confident there is local support for your project?": False
    },
    "project-qualification": {
        "Does your project meet the definition of a subsidy?": False
    },
    "skills-and-resources": {
        "Do you have experience of managing a community asset?": False,
        "Do you have any plans to recruit people to help you manage the asset?": False,
    },
    "upload-business-plan": {"Upload business plan": "sample1.doc"},
    "project-information": {
        "Have you been given funding through the Community Ownership Fund before?": False,
        "Project name": "Restore the beautiful museum in Bristol",
        "Tell us how the asset is currently being used, or how it has been used before, and why it's important to the community": (
            "Test"
        ),
        "Explain why the asset is at risk of being lost to the community, or why it has already been lost": (
            "Test"
        ),
        "Give a brief summary of your project, including what you hope to achieve": (
            "Test"
        ),
        "Address of the community asset": (
            "Test Address, null, Test Town Or City, null, QQ12QQ"
        ),
        "In which constituency is your asset?": "Constituency",
        "In which local council area is your asset?": "Local Council",
    },
    "organisation-information": {
        "Your unique tracker number": "ANON-###-###-###",
        "Organisation name": "Test",
        "Does your organisation use any other names?": False,
        "What is your organisation's main purpose?": "Test",
        "Tell us about your organisation's main activities": "Test",
        "Tell us about your organisation's main activities - Activity 2 ": "",
        "Tell us about your organisation's main activities - Activity 3 ": "",
        "Have you delivered projects like this before?": False,
        "Type of organisation": "CIO",
        "Charity number ": "Test",
        "Is your organisation a trading subsidiary of a parent company?": False,
        "Organisation address": (
            "Test Address, null, Test Town Or City, null, QQ12QQ"
        ),
        "Is your correspondence address different to the organisation address?": False,
        "Website and social media ": "https://twitter.com/luhc",
        "Website and social media - Link or username 2": "",
        "Website and social media - Link or username 3": "",
        "Is your application a joint bid in partnership with other organisations?": False,
    },
    "applicant-information": {
        "Name of lead contact": "Test Name",
        "Lead contact email address": (
            "testemailfundingservice@testemailfundingservice.com"
        ),
        "Lead contact telephone number": "0000000000",
    },
    "asset-information": {
        "Asset type": "museum",
        "What do you intend to do with the asset?": "buy-the-asset",
        "Do you know who currently owns your asset?": False,
        "Describe the current ownership status": "Current Owner",
        "Have you already completed the purchase or lease?": False,
        "Describe the expected sale process, or the proposed terms of your lease if you are renting the asset": (
            "Test"
        ),
        "Expected date of sale or lease": "2022-12-01",
        "Is your asset currently publicly owned?": False,
        "Is this a registered Asset of Community Value (ACV)?": False,
        "Is the asset listed for disposal, or part of a Community Asset Transfer?": False,
        "Why is the asset at risk of closure?": [
            "for-sale-or-listed-for-disposal"
        ],
    },
    "community-engagement": {
        "Tell us how you have engaged with the community about your intention to take ownership of the asset, and explain how this has shaped your project plans": (
            "Tell us how you have engaged with the community about your"
            " intention to take ownership of the asset"
        ),
        "Have you done any fundraising in the community?": False,
        "Tell us how your project supports any wider local plans": (
            "Tell us how your project supports any wider local plans"
        ),
    },
    "funding-required": {
        "Capital funding": "2300",
        "Revenue funding (optional)": "2300",
        "Capital costs": ["Capital Funding : \\u00a32300"],
        "Are you applying for revenue funding from the Community Ownership Fund? (optional)": False,
        "Have you secured any match funding yet?": False,
        "Do you have any match funding identified but not yet secured?": False,
        "Asset value": "2300",
    },
    "community-benefits": {
        "What community benefits do you expect to deliver with this project? ": [
            "community-pride"
        ],
        "Tell us about these benefits in detail, and explain how you'll measure the benefits it'll bring for the community": (
            "Test"
        ),
        "Explain how you plan to sustain, and potentially expand, these benefits over time": (
            "Test"
        ),
        "Tell us how you'll make sure the whole community benefits from the asset": (
            "Test"
        ),
    },
    "inclusiveness-and-integration": {
        "Describe the planned activities or services that will take place at the asset": (
            "Test"
        ),
        "Describe anything that might prevent people from using the asset or participating in its running": (
            "Test"
        ),
        "Tell us how you'll make your project accessible and inclusive to everyone in the community": (
            "Test"
        ),
        "Describe how the project will bring people together from all over the community": (
            "Test"
        ),
    },
    "project-costs": {
        "Summarise your cash flow for the running of the asset": "Test",
        "If successful, will you use your funding in the next 12 months?": False,
        "Sources of income": ["Income Test : \\u00a32300"],
        "Running costs": ["Running Cost Test : \\u00a32300"],
    },
    "community-representation": {
        "List the members of your board": "Test",
        "Tell us about your governance and membership structures": "Test",
        "Explain how you'll consider the views of the community in the running of the asset": (
            "Test"
        ),
    },
    "value-to-the-community": {
        "Tell us about your local community as a whole": "Test",
        "Describe any specific challenges your community faces, and how the asset will address these": (
            "Test"
        ),
    },
    "declarations": {
        "Confirm you have considered subsidy control and state aid implications for your project, and the information you have given us is correct": True,
        "Confirm you have considered people with protected characteristics throughout the planning of your project": False,
        "Confirm you have considered sustainability and the environment throughout the planning of your project, including compliance with the government's Net Zero ambitions": True,
        "Confirm you have a bank account set up and associated with the organisation you are applying on behalf of": False,
    },
}
