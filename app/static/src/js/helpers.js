AssessFrontend.removeAttributeValue = function(el, attr, value) {
  let re, m;
  if (el.getAttribute(attr)) {
    if (el.getAttribute(attr) == value) {
      el.removeAttribute(attr);
    } else {
      re = new RegExp('(^|\\s)' + value + '(\\s|$)');
      m = el.getAttribute(attr).match(re);
      if (m && m.length == 3) {
        el.setAttribute(attr, el.getAttribute(attr).replace(re, (m[1] && m[2])?' ':''))
      }
    }
  }
}

AssessFrontend.addAttributeValue = function(el, attr, value) {
  let re;
  if (!el.getAttribute(attr)) {
    el.setAttribute(attr, value);
  }
  else {
    re = new RegExp('(^|\\s)' + value + '(\\s|$)');
    if (!re.test(el.getAttribute(attr))) {
      el.setAttribute(attr, el.getAttribute(attr) + ' ' + value);
    }
  }
};

AssessFrontend.nodeListForEach = function (nodes, callback) {
    if (window.NodeList.prototype.forEach) {
        return nodes.forEach(callback)
    }
    for (let i = 0; i < nodes.length; i++) {
        callback.call(window, nodes[i], i, nodes)
    }
};

const showTagsElement = document.getElementById("show-tags");
if (showTagsElement) {
    showTagsElement.addEventListener("change", (event) => {
        const allTagDetails = Array.from(document.getElementsByClassName("dlhuc-tag-expand"));
        const checkboxState = event.target.checked;
        allTagDetails.forEach(tagDetail => {
            tagDetail.open = checkboxState;
        });
    });
}

// This is a temporary fix to ensure tab changing works for flag history.
// Updating to `4.7.0` for govuk css broke this functionality. (v0.0.252)
// Upgrading `govuk-frontend-jinja==2.7.0` (the equivalent 4.7.0 version) does not fix it.
const tabs = document.querySelectorAll('[id^="tab"]');
const tabAnchors = document.querySelectorAll('.govuk-tabs__tab');
Array.from(tabAnchors).forEach(tabAnchor => {
    tabAnchor.addEventListener('click', (tabAnchorElement) => {
        const hash = tabAnchorElement.target.hash;
        if (hash) {
            Array.from(tabs).forEach((tab) => {
                tab.classList.add('govuk-tabs__panel--hidden');
            });
            Array.from(tabAnchors).forEach((tabA) => {
               tabA.parentElement.classList.remove('govuk-tabs__list-item--selected')
            });

            const activeTab = document.getElementById(hash.replace('#', ''));
            activeTab.classList.remove('govuk-tabs__panel--hidden');
            tabAnchorElement.target.parentElement.classList.add('govuk-tabs__list-item--selected');
        }
    });
})


function toggleAccordionOff(accordion, index) {
    const content = document.getElementById(`accordion-default-content-${index}`);
    content.style.display = ''; // Set display to empty to hide the content
    const textSpan = accordion.querySelector('.govuk-accordion__section-toggle-text');
    textSpan.textContent = 'Show'; // Change the text to 'Show'
    const chavron = accordion.querySelector('.govuk-accordion-nav__chevron');
    chavron.classList.add('govuk-accordion-nav__chevron--down'); // Add the class to change the chevron direction
}

function toggleAccordionOn(accordion, index) {
    const content = document.getElementById(`accordion-default-content-${index}`);
    content.style.display = 'block'; // Set display to 'block' to show the content
    const textSpan = accordion.querySelector('.govuk-accordion__section-toggle-text');
    textSpan.textContent = 'Hide'; // Change the text to 'Hide'
    const chavron = accordion.querySelector('.govuk-accordion-nav__chevron');
    chavron.classList.remove('govuk-accordion-nav__chevron--down'); // Remove the class to change the chevron direction
}

function toggleAccordion(accordion, index) {
    const content = document.getElementById(`accordion-default-content-${index}`);
    if (content.style.display) {
        toggleAccordionOff(accordion, index);
    } else {
        toggleAccordionOn(accordion, index);
    }
}

const closedAccordionButtons = Array.from(document.getElementsByClassName('landing-accordion'))
closedAccordionButtons.forEach((accordion, index) => {
    accordion.onclick = (_e) => {
        toggleAccordion(accordion, index + 1);
    }
})

const showAllAccordion = document.querySelector('.govuk-accordion__show-all');
if (showAllAccordion) {
    showAllAccordion.toggledOn = false;
    showAllAccordion.onclick = (_e) => {
        showAllAccordion.toggledOn = !showAllAccordion.toggledOn;
        const showAllText = showAllAccordion.querySelector('.govuk-accordion__show-all-text');
        const showAllChavron = showAllAccordion.querySelector('.govuk-accordion-nav__chevron');
        if (showAllAccordion.toggledOn) {
            closedAccordionButtons.forEach((accordion, index) => {
                toggleAccordionOn(accordion, index + 1);
            })
            showAllText.textContent = 'Hide all sections';
            showAllChavron.classList.remove('govuk-accordion-nav__chevron--down');
        } else {
            closedAccordionButtons.forEach((accordion, index) => {
                toggleAccordionOff(accordion, index + 1);
            })
            showAllText.textContent = 'Show all sections';
            showAllChavron.classList.add('govuk-accordion-nav__chevron--down');
        }
    }
}
