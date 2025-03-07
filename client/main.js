const decideDefaultLanguage = async (indexes) => {
	/** 
	 *	Takes the returned list of language indexes
	 *	and chooses a default language based on user preferences
	 */ 
	console.log("decideDefaultLanguage()");

	var enabledLanguages = Object.keys(indexes);
	// Is there only one? 
	if (enabledLanguages.length == 1) {
		var currentLanguage = enabledLanguages[0];
		localStorage.setItem("currentLanguage", currentLanguage);
		return currentLanguage;
	}

	// Is one being passed in the URL?
	var currentLanguage = findGetParameter("language");
	if(currentLanguage != false) {
		if(indexes[currentLanguage]) {
			return currentLanguage;
		}
	}

	// Is one already set and is it in the browser? 
	var currentLanguage = localStorage.getItem("currentLanguage");
	if(currentLanguage != false) {
		if(indexes[currentLanguage]) {
			return currentLanguage;
		}
	}

	// What languages is the browser set to?
	const intersectionLanguages = enabledLanguages.filter(
		value => window.navigator.languages.includes(value)
	);
	
	// Take the intersection with what languages we have and
	// return one at random
	if(intersectionLanguages.length > 0) {
		var currentLanguage = intersectionLanguages[getRandomInt(0, intersectionLanguages.length - 1)];
		localStorage.setItem("currentLanguage", currentLanguage);
		return currentLanguage
	}

	// Choose the first non-English one
	for(var language in enabledLanguages) {
		if(language != "en") {
			localStorage.setItem("currentLanguage", language);
			return language;
		}
	}
}

const getIndexes = async () => {
	// Creates the language selection dialogue
	console.log("getIndexes()");

	const indexesPromise = fetch(STATIC_URL + "/indexes");
	const indexes = await Promise.all([indexesPromise]);
	const indexesData = indexes.map(response => response.json());
	const allData = await Promise.all(indexesData);

	return allData[0];
}

const populateLanguageSelector = async (indexes, defaultLanguage) => {
	console.log("populateLanguageSelector()");
	languageSelector = document.getElementById("languages");

	var enabled = "";
	for(var language in indexes) {
			enabled += language + " ";
			var languageElem = document.createElement("option");
			var languageText = document.createTextNode(indexes[language]["display"]); // Display name
			if(defaultLanguage == language) {
				languageElem.setAttribute("selected","");
			}
			languageElem.setAttribute("value", language);
			languageElem.appendChild(languageText);
			languageSelector.appendChild(languageElem);
	}
	console.log("  [languages] "  + enabled);
}

const runLanguage = async (language, acceptingChars) => {

	document.omnilingo = new OmniLingo();

	document.omnilingo.setup(STATIC_URL, language);

	document.omnilingo.cleanup();

	var h = document.documentElement;
	if(language == "ar" || language == "fa" || language == "dv") { // FIXME: be cleverer here
		// <html dir="rtl" language="ar">
		h.setAttribute('dir', 'rtl');
	} else {
		h.setAttribute('dir', 'ltr');
	}
	h.setAttribute('lang', language);

	document.omnilingo.setEquivalentChars(acceptingChars);

	await document.omnilingo.fetchIndex();

	// Get the current level

	document.omnilingo.run();	
}

const main = async () => {

	var indexes = await getIndexes();

	var defaultLanguage = await decideDefaultLanguage(indexes);

	console.log("  [defaultLanguage] " + defaultLanguage);

	populateLanguageSelector(indexes, defaultLanguage);

	window.onkeydown = globalKeyDown;

	var acceptingChars = indexes[defaultLanguage]["accept"];

	runLanguage(defaultLanguage, acceptingChars);
}

window.onload = main;
