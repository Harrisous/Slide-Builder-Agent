Solstice Onsite | Applied ML Engineer | Harry Li
Overall Goal

Build a pipeline to create a multi-slide deck for a particular drug, Fruzaqla (http://fruzaqlahcp.com/), based on a user query. 

You will be given an existing set of resources for Fruzaqla including: 
1. Clinical papers about the therapeutic 
2. Content that has been created for the drug already 
3. Style guide for this brand. 

Your task is to take these inputs and leverage them so that the user can provide an instruction like “Make me a 3 slide presentation focusing on Fruzaqla study design, efficacy results, and safety” and receive an output in html format of said presentation. 

Additional Context: 
Content must be derived from previously approved components. Very importantly, given the regulated nature of the industry, text content must be created from previously approved claims (text that has been used previously by the team in other pieces) or derived from clinical literature. Similarly, visual elements (icons, logos, graphs, figures) must be previously approved. we cannot create net new visuals. Any 
Slides need to be relevant to the user query, complementary of each other, and visually cohesive.  As you get started, think through some of the complexities of a multi-slide deck made by agents and how that differs from considerations of a single slide output. What additional tools would you need? What things do you need to check for to ensure consistency across slides? How can we ensure that content across slides is complementary and not duplicative?
Here is an example of a deck for reference. 

Final Deliverable
-	Python Zip Folder with fully functional pipeline that can take in any query regarding Fruzaqla and output an HTML presentation.

Logistics
-	You will be given:
-	OpenAI API key (in Appendix below) as well as API keys for any other commercial LLM you would like upon request
-	The inputs described above (clinical papers, prior approved content, and style guide)
-	Pinecone API key or API key to any other VectorDB (if needed)
-	Anything else you need
-	You may use AI however you would like. Please make sure you understand the code as we will ask you a bunch of questions about it and will test your understanding of what you (or your AI) has written
-	We do have an existing platform and flow that handles the functionality you will working on today. To allow you to think independently and from first principles, we won’t share with you how we currently handle this process until the end of our day together. However, any questions you have about the users’ needs please do clarify with us. 
-	 You will have from the beginning of the day until the end of the day to finish this project. “End of Day” can be dictated by you but people typically finish around 4-6ish. 
-	Once you feel ready – we will go over the project with you as a team. You will have an opportunity to walk through what you built as well as your rationale for why you constructed things the way you did. Team members will ask a bunch of questions, both about your specific choices as well as general questions about coding and AI fundamentals. You will also have an opportunity to ask anything you’d like about Solstice.
-	Ari will be your point of contact for any questions you have. Feel free to use him as much as you would like. If there’s a point of confusion, we’d rather you get it resolved at the beginning of the day then at the end. 
-	Lunch is on us. Let (Yiwen or Aris) know when you are hungry and we can pick something up together.

Evaluation Criteria
-	Clarity and Depth of Thought. This is by the far the most important thing we are looking for. How deeply did you think through the flow you built? Why did you add certain nodes to your pipeline? How did you decide what LLMs to use? How deeply have you thought about edge cases? Where can you take this pipeline from here?  More than anything you build, how you talk about what you built is how we assess depth of thought.
-	Technical Prowess. Does what you built work? We know nothing you develop in a few hours is going to be perfect but does it function properly? Do you know how your code works? Does the syntax make sense? Can you describe what individual functions do? How would you turn this into scalable, production-ready from here? While less important than depth of thinking, this is something we will evaluate deeply both through your code and your answers to our questions. 



Appendix (Keys and Example Slides)

API KEYS:
OPENAI_API_KEY: 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

PINECONE_API_KEY: pcsk_6xCFMX_EFxJCpnVjGj2irxnF9u6Em74vA8WLrvxfSKej24GrZAYpzw7dw9K2PjezKrrPSh

PINECONE INDEX NAMES: 
-> content-gen-group-index
example entry in db: 
	metadata:
■	brand_id: "0882bf98-8a98-4446-927b-de408aea5759"
■	claims: [ "4023e523-66b9-472f-9042-15840301192b", "e70827e7-d2d3-4bd6-8b5c-9d8197c45d74", "c20164e7-0928-467a-af50-cdf83b1257ab" ]
■	claims_count: 3
■	context: "Exploratory Efficacy Outcomes of ORSERDU in ER+/HER2- Advanced Breast Cancer Patients Previously Treated with Endocrine Therapy and CDK4/6 Inhibitors: Progression-Free Survival Analyses and Subgroup Data from the EMERALD Trial"
■	group_description: "Exploratory Efficacy Outcomes of ORSERDU in ER+/HER2- Advanced Breast Cancer Patients Previously Treated with Endocrine Therapy and CDK4/6 Inhibitors: Progression-Free Survival Analyses and Subgroup Data from the EMERALD Trial"
■	group_id: "9acd36cd-b648-4487-abd9-9f3c39d3ab79" 
	
-> content-gen-claim-index
example entry in db:
●	metadata:
■	brand_id: "0882bf98-8a98-4446-927b-de408aea5759"
■	claim_id: "4023e523-66b9-472f-9042-15840301192b"
■	claim_text: "8.6 months mPFS in patients treated with prior ET + CDK4/6i for 12 months or more7\nResults of this exploratory post hoc analysis are descriptive but not conclusive of efficacy, are not controlled for type 1 error, and require cautious interpretation. Small patient numbers can be a limitation of subgroup analyses and could represent chance findings.\nEXPLORATORY POST HOC ANALYSIS: mPFS IN PATIENTS WITH PRIOR ET + CDK4/6i FOR >12 MONTHS7"
■	claim_type: "OTHER"
■	content: "8.6 months mPFS in patients treated with prior ET + CDK4/6i for 12 months or more7\nResults of this exploratory post hoc analysis are descriptive but not conclusive of efficacy, are not controlled for type 1 error, and require cautious interpretation. Small patient numbers can be a limitation of subgroup analyses and could represent chance findings.\nEXPLORATORY POST HOC ANALYSIS: mPFS IN PATIENTS WITH PRIOR ET + CDK4/6i FOR >12 MONTHS7"
■	content_type: "sectionHeading"
■	context: "8.6 months mPFS in patients treated with prior ET + CDK4/6i for 12 months or more7\nResults of this exploratory post hoc analysis are descriptive but not conclusive of efficacy, are not controlled for type 1 error, and require cautious interpretation. Small patient numbers can be a limitation of subgroup analyses and could represent chance findings.\nEXPLORATORY POST HOC ANALYSIS: mPFS IN PATIENTS WITH PRIOR ET + CDK4/6i FOR >12 MONTHS7"
■	css_styles: "/* ------------- CSS RESET (minimal) ------------- */\n*,\n*::before,\n*::after{\n box-sizing:border-box;\n margin:0;\n padding:0;\n}\n\n/* ------------- DESIGN TOKENS ------------- */\n:root{\n /* colors */\n --green:#00723B;\n --navy:#0A2342;\n --black:#000;\n --white:#fff;\n\n /* typography */\n --font-base:'Helvetica Neue',Arial,sans-serif;\n --h1-size:clamp(2.25rem,5vw + 1rem,2.5rem); /* 36-40px depending on viewport */\n --p-size:1rem; /* 16px */\n --banner-size:1.125rem; /* 18px */\n\n /* spacing */\n --gap-lg:3rem; /* 48px */\n --gap-md:1.875rem; /* 30px */\n --gap-sm:1rem; /* 16px */\n\n /* other */\n --pill-radius:9999px;\n}\n\n/* ------------- LAYOUT ------------- */\n.section{\n max-width:1200px;\n margin-inline:auto;\n padding-inline:var(--gap-sm);\n padding-block:var(--gap-lg);\n display:flex;\n flex-direction:column;\n gap:var(--gap-lg);\n}\n\n/* ------------- TYPOGRAPHY ------------- */\n.section__title{\n font-family:var(--font-base);\n font-size:var(--h1-size);\n line-height:1.2;\n font-weight:700;\n color:var(--green);\n}\n\n.section__title sup{\n font-size:0.45em;\n vertical-align:super;\n}\n\n.section__text{\n font-family:var(--font-base);\n font-size:var(--p-size);\n line-height:1.5;\n font-weight:500;\n color:var(--black);\n max-width:100ch; /* prevent ultra-long lines */\n}\n\n/* ------------- BANNER ------------- */\n.section__banner{\n background-color:var(--navy);\n color:var(--white);\n padding-block:var(--gap-md);\n padding-inline:var(--gap-sm);\n text-align:center;\n border-radius:var(--pill-radius);\n width:100%;\n overflow:hidden; /* hide any radius artefacts on small screens */\n}\n\n.section__banner-text{\n font-family:var(--font-base);\n font-size:var(--banner-size);\n line-height:1.3;\n font-weight:700;\n letter-spacing:0.5px;\n text-transform:uppercase;\n}\n\n.section__banner-text .lowercase{\n text-transform:none; /* preserve lower-case “m” */\n}\n\n.section__banner-text sup{\n font-size:0.45em;\n vertical-align:super;\n}\n\n/* ------------- RESPONSIVE ------------- */\n@media(max-width:768px){\n .section{\n padding-inline:var(--gap-sm);\n gap:var(--gap-md);\n }\n\n .section__title{\n font-size:clamp(1.75rem,6vw + 0.5rem,2rem); /* 28-32px */\n }\n\n .section__banner-text{\n font-size:1rem; /* 16px */\n }\n}"
■	group_id: "9acd36cd-b648-4487-abd9-9f3c39d3ab79"
■	html_content: "<section class=\"section\">\n <h1 class=\"section__title\">\n 8.6 months mPFS in patients treated with prior ET + CDK4/6i for 12 months or more<sup>7</sup>\n </h1>\n\n <p class=\"section__text\">\n Results of this exploratory post hoc analysis are descriptive but not conclusive of efficacy, are not controlled for type&nbsp;1 error, and require cautious interpretation. Small patient numbers can be a limitation of subgroup analyses and could represent chance findings.\n </p>\n\n <div class=\"section__banner\">\n <p class=\"section__banner-text\">\n EXPLORATORY POST HOC ANALYSIS: <span class=\"lowercase\">mPFS</span> IN PATIENTS WITH PRIOR ET + CDK4/6i FOR ≥12 MONTHS<sup>7</sup>\n </p>\n </div>\n</section>"
■	polygon: "[[8.5927, 56.7777], [45.7636, 56.7777], [45.7636, 65.2193], [8.5927, 65.2193]]"

Both are related together with group id.


ID: 1a2be2ee-281a-48fd-b4f5-db86a46c9d07
•	brand_id: "0882bf98-8a98-4446-927b-de408aea5759"
•	claim_id: "1a2be2ee-281a-48fd-b4f5-db86a46c9d07"
•	claim_text: "[COMPANY LOGO] Stemline, a Menarini Group Company."
•	claim_type: "OTHER"
•	content: "[COMPANY LOGO] Stemline, a Menarini Group Company."
•	content_type: "figure"
•	context: "[COMPANY LOGO] Stemline, a Menarini Group Company."
•	css_styles: ""
•	group_id: "813b103f-4c1d-4b3d-a7fc-279e3c41ad1c"
•	html_content: ""
•	image_url: "https://solstice-public-forever.s3.us-east-1.amazonaws.com/0882bf98-8a98-4446-927b-de408aea5759/ebdf339c-aa08-4880-8d1a-217d509439db.png"
•	polygon: "[[46.5746, 343.116], [53.0475, 343.1151], [53.0492, 345.5313], [46.5762, 345.5321]]"



fruzaqlahcp.com
