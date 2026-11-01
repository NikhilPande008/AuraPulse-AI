"""Centralized messages and suggested ideas for offline copilot responses."""

DECLINE_MESSAGES: dict[str, str] = {
    "mr": (
        "मी केवळ कार्यक्रम नियोजन, बजेट, वेळापत्रक आणि पुरवठादार व्यवस्थापनात मदत करतो. "
        "कार्यक्रमाव्यतिरिक्त इतर विनंत्या हाताळण्यात मी असमर्थ आहे."
    ),
    "hi": (
        "मैं विशेष रूप से कार्यक्रम योजना, बजट, समय-सीमा और विक्रेता प्रबंधन में सहायता करता हूँ। "
        "मैं कार्यक्रम से बाहर के अनुरोधों में सहायता करने में असमर्थ हूँ।"
    ),
    "en": (
        "I specialize exclusively in event planning, budgeting, timeline scheduling, and vendor logistics. "
        "I cannot assist with requests outside of organizing your event."
    ),
}

DATE_PAST_WARNINGS: dict[str, str] = {
    "mr": "त्रुटी: कार्यक्रमाची तारीख {target_date} वर हलवता येणार नाही कारण ही तारीख भूतकाळातील आहे. कृपया भविष्यातील तारीख निवडा.",
    "hi": "त्रुटि: कार्यक्रम की तिथि {target_date} को नहीं बदला जा सकता क्योंकि यह तारीख बीत चुकी है। कृपया भविष्य की तारीख चुनें।",
    "en": "Error: Cannot move event date to {target_date} because it is in the past or today. Please choose a future date.",
}

DATE_REPLIES: dict[str, str] = {
    "mr": "कार्यक्रमाची तारीख बदलून {target_date} केली आहे. रिव्हर्स माइलस्टोन्स आणि वेळापत्रक पुन्हा मोजण्यात आले आहे.",
    "hi": "कार्यक्रम की तिथि बदलकर {target_date} कर दी गई है। सभी मील के पत्थर और समय-सीमा नए सिरे से निर्धारित किए गए हैं।",
    "en": "Rescheduled event date to {target_date}. Backwards milestones and timeline have been dynamically recalculated.",
}

DATE_IDEAS: dict[str, list[str]] = {
    "mr": [
        "नवीन तारखेसाठी ({target_date}) हॉल आणि केटररची उपलब्धता तपासा",
        "निमंत्रण पत्रिकांवर नवीन तारीख अद्यतनित करा",
    ],
    "hi": [
        "नई तिथि ({target_date}) के लिए स्थल और केटरर की पुष्टि करें",
        "डिजिटल निमंत्रण में संशोधित तिथि अपडेट करें",
    ],
    "en": [
        "Confirm venue and primary vendor availability for {target_date}",
        "Issue revised RSVP notices with updated celebration date",
    ],
}

BUDGET_CUT_REPLIES: dict[str, str] = {
    "mr": "बजेट {abs_pct:.0f}% ने यशस्वीपणे कमी केले आहे. महत्त्वाचे सुरक्षा आणि मुख्य केटरिंग बाबी १००% सुरक्षित आहेत. खर्च ₹{total:,.2f} पर्यंत समायोजित केला आहे.",
    "hi": "बजट {abs_pct:.0f}% कम कर दिया गया है। महत्वपूर्ण सुरक्षा और मुख्य खानपान की वस्तुएं पूरी तरह सुरक्षित हैं। अब कुल अनुमानित खर्च ₹{total:,.2f} है।",
    "en": (
        "Successfully scaled budget by {pct:.0f}%. Critical safety & primary catering items remain intact. "
        "Expenditure adjusted to ₹{total:,.2f} against a ceiling of ₹{limit:,.2f}."
    ),
}

BUDGET_CUT_IDEAS: dict[str, list[str]] = {
    "mr": [
        "डिफ व्हिज्युअलायझरमध्ये सुधारित तपशील तपासा",
        "फ्लोरल आणि तंत्रज्ञान पुरवठादारांशी दरांवर चर्चा करा",
    ],
    "hi": [
        "डिफ विज़ुअलाइज़र में बदले हुए मदों की जांच करें",
        "पुनर्निर्धारित बजट को आकस्मिक फंड में आवंटित करें",
    ],
    "en": [
        "Review adjusted line item totals in the Diff Visualizer",
        "Confirm revised purchase orders with floral and lighting leads",
    ],
}

HEADCOUNT_RANGE_WARNINGS: dict[str, str] = {
    "mr": "चेतावणी: पाहुण्यांची संख्या १ ते १०,००० च्या दरम्यान असावी (प्रयत्न: {target_hc}). सध्याची संख्या {old_hc} पाहुणे तशीच ठेवली आहे.",
    "hi": "चेतावनी: अतिथियों की संख्या 1 और 10,000 के बीच होनी चाहिए (प्रयास: {target_hc})। वर्तमान अतिथि संख्या {old_hc} यथावत रखी गई है।",
    "en": "Warning: Guest headcount must be between 1 and 10,000 (attempted: {target_hc}). Plan remains at {old_hc} guests.",
}

HEADCOUNT_REPLIES: dict[str, str] = {
    "mr": "पाहुण्यांची संख्या {old_hc} वरून {target_hc} पर्यंत अद्यतनित केली आहे. केटरिंग आणि इतर बाबी त्यानुसार समायोजित केल्या आहेत.",
    "hi": "अतिथियों की संख्या {old_hc} से बदलकर {target_hc} कर दी गई है। प्रति व्यक्ति खानपान की मात्रा उसी अनुसार समायोजित की गई है।",
    "en": "Updated guest headcount from {old_hc} to {target_hc} pax. Per-head catering quantities adjusted proportionally.",
}

HEADCOUNT_IDEAS: dict[str, list[str]] = {
    "mr": [
        "{target_hc} पाहुण्यांसाठी बैठक व्यवस्था आणि हॉल क्षमता तपासा",
        "सुधारित संख्येनुसार रिटर्न गिफ्ट्सची संख्या समायोजित करा",
    ],
    "hi": [
        "{target_hc} अतिथियों के लिए हॉल बैठक व्यवस्था की पुष्टि करें",
        "संशोधित संख्या के अनुसार स्वागत उपहारों की गणना करें",
    ],
    "en": [
        "Confirm venue banquet seating arrangement for {target_hc} guests",
        "Recalculate guest welcome gift quantities",
    ],
}

CATERING_REPLIES: dict[str, str] = {
    "mr": "मी आपल्या इव्हेंटच्या मेनूमध्ये अस्सल महाराष्ट्रीयन मेजवानी समाविष्ट केली आहे! मेनूमध्ये साजूक तुपातील पुरणपोळी, कटाची आमटी आणि उकडीचे मोदक समाविष्ट केले आहेत.",
    "hi": "मैंने खानपान अनुभाग को प्रामाणिक शाकाहारी महाराष्ट्रीयन दावत में बदल दिया है! मेनू में अब शुद्ध देसी घी की पूरन पोली, ककड़ी कोशिंबीर और उकडीचे मोदक शामिल हैं।",
    "en": "I have upgraded the catering section to an authentic regional banquet with live culinary counters.",
}

CATERING_IDEAS: dict[str, list[str]] = {
    "mr": [
        "सजावटीसाठी पारंपारिक पितळी समया आणि झेंडूच्या फुलांचा वापर करा",
        "स्वागत पेय म्हणून मातीच्या कुल्हडमध्ये सोलकढी सर्व्ह करा",
        "जेवणाच्या टेबलवर केळीच्या पानांची सजावट करा",
    ],
    "hi": [
        "पारंपरिक स्वागत के लिए मिट्टी के कुल्हड़ में सोलकढ़ी परोसें",
        "भोजन क्षेत्र में लाइव मोदक मेकिंग काउंटर स्थापित करें",
        "पारंपरिक अनुभव के लिए तांबे के बर्तनों में भोजन परोसें",
    ],
    "en": [
        "Set up a live Ukdiche Modak counter where guests can watch artisanal shaping",
        "Serve refreshing Solkadhi shooters in clay kulhads as welcome drinks",
        "Arrange banana-leaf table runner accents for the banquet buffet",
    ],
}

FLORAL_SAX_REPLY = "Reduced floral budget by 20% and added a live solo saxophonist for sunset and cocktail hours."
FLORAL_SAX_IDEAS = [
    "Position the solo saxophonist near the outdoor aperitif bar for golden hour acoustic ambience",
    "Coordinate custom jazz and soul setlist with the sound technician",
    "Review reduced floral table arrangements with botanical florist",
]

GAMES_REPLY = "Added an interactive Game Master and curated 5 customized party games for the celebration."
GAMES_IDEAS = [
    "Trivia Roasts: Milestone trivia quiz customized with nostalgic host moments",
    "Neon Scavenger Hunt: Glow-in-the-dark clues hidden across the venue",
    "Lip Sync Battle: Timed team performances with novelty props and stage lighting",
    "Retro Arcade Tournament: High-score mini challenges on tabletop consoles",
    "Rapid-Fire Photo Booth Bingo: Guests race to snap pics with 5 quirky props",
]

RITUALS_REPLY = (
    "Added Sakhar Puda engagement ritual and pooja samagri audit milestone to the backwards planning roadmap."
)
RITUALS_IDEAS = [
    "Book traditional Shehnai and Chaughada musicians for the Sakhar Puda entrance",
    "Prepare decorative sugar cone packages (Sakhar Puda hampers) for family gifting",
    "Reconfirm pooja items list with family pandit 3 weeks in advance",
]

DEFAULT_REPLIES: dict[str, str] = {
    "mr": "मी आपल्या '{prompt}' विनंतीचे पुनरावलोकन केले आहे. सध्याचा खर्च ₹{total:,.2f} आहे.",
    "hi": "मैंने आपके अनुरोध '{prompt}' की समीक्षा की है। वर्तमान अनुमानित खर्च ₹{total:,.2f} है।",
    "en": (
        "I reviewed your request '{prompt}' against '{title}'. "
        "Your current estimated spend is ₹{total:,.2f} against a ceiling of ₹{limit:,.2f}."
    ),
}

DEFAULT_IDEAS: dict[str, list[str]] = {
    "mr": ["कार्यक्रमाच्या तारखा आणि बजेट मर्यादा तपासा"],
    "hi": ["आवश्यकतानुसार बजट या कार्यक्रम की तिथि में बदलाव करें"],
    "en": [
        "Audit vendor contracts 14 days prior to event to lock contingency thresholds",
        "Introduce digital QR-code schedules for real-time guest transitions",
    ],
}

SUGGESTED_IDEAS_BY_LANG: dict[str, list[str]] = {
    "mr": [
        "सजावटीसाठी पारंपरिक झेंडू आणि पितळी समयांची मांडणी करा",
        "कार्यक्रमाच्या शेवटी पाहुण्यांसाठी पारंपरिक भेटवस्तूंचे नियोजन करा",
    ],
    "hi": [
        "अतिथि स्वागत के लिए लाइव ढोल-ताशा या पारंपरिक संगीत का समन्वय करें",
        "अंतिम समय के खर्चों के लिए 5% बजट आकस्मिक रिजर्व में सुरक्षित रखें",
    ],
    "en": [
        "Audit vendor contracts 14 days prior to event to lock cancellation terms",
        "Introduce digital QR-code schedules so guests receive real-time notifications",
        "Reserve 5% buffer allocation exclusively for unforeseen electrical requirements",
    ],
}
