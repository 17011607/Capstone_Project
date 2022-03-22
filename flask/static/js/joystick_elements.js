/*
	jquery-element - 1.7.0
	https://github.com/jquery-element/jquery-element
*/

(function( $ ) {

"use strict";

var
	// Because we can't call `arguments.slice()`
	arraySlice = [].slice,
	list_elemName = {}
;

function initElement( obj, el ) {
	var
		html,
		elementObject,
		elNextNode,
		jqHtml,
		jqNestedParent,
		jqElementParent,
		jqElementNext,
		jqElement = $( el ),
		containerClasses = el.dataset[ "jqueryElementClass" ]
	;

	// Remove the data-jquery-element attribute to not re-initialize it
	// when the element is detach and reattach to the DOM again.
	delete el.dataset[ "jqueryElement" ];
	delete el.dataset[ "jqueryElementClass" ];

	// if there is some HTML to include inside the jqElement.
	if ( html = obj.html ) {
		jqElement.html( html );
	}

	// If there is some HTML to replace the jqElement.
	if ( html = obj.htmlReplace ) {

		// Creation of the content.
		jqHtml = $( html );

		// If the jqElement will NOT be inside this new content...
		if ( html.indexOf( "{{html}}" ) < 0 ) {

			// ...we delete it by .replaceAll.
			jqElement = jqHtml.replaceAll( el );
		} else {

			// Searching of the parent element who are containing
			// the textNode with "{{html}}" inside.
			jqNestedParent = jqHtml.find( ":contains('{{html}}'):last" );
			if ( !jqNestedParent.length ) {
				jqNestedParent = jqHtml;
			}

			jqElementParent = jqElement.parent();
			jqElementNext = jqElement.next();

			// Find the textNode...
			elNextNode = jqNestedParent[ 0 ].firstChild;
			for ( ; elNextNode ; elNextNode = elNextNode.nextSibling ) {
				if ( elNextNode.nodeType === 3 && // Node.TEXT_NODE = 3
					elNextNode.textContent.indexOf( "{{html}}" ) >= 0
				) {

					// ...to be deleted and replaced by the jqElement.
					jqElement.replaceAll( elNextNode );
					break;
				}
			}

			// Now, all the content (with the jqElement inside)
			// will take the old position in the DOM of jqElement.
			jqElement = jqHtml;
			if ( jqElementNext.length ) {
				jqElement.insertBefore( jqElementNext );
			} else {
				jqElement.appendTo( jqElementParent );
			}
		}
	}

	// Add the classes inside the [data-jquery-element-class] on the container.
	jqElement.addClass( containerClasses );

	// Extend the `this` Object with all the methodes of the `prototype:` object.
	elementObject =
	jqElement[ 0 ].jqueryElementObject = $.extend( {
		jqElement: jqElement
	}, obj.prototype );

	// Call the element's constructor: the `init:` function.
	if ( obj.init ) {
		obj.init.call( elementObject );
	}
}

// This code is critical because it's called every time a new DOM element
// is inserted or removed. Try to note use jQuery inside.
if ( MutationObserver = MutationObserver || WebKitMutationObserver ) {
	new MutationObserver( function( mutations ) {
		var i = 0, j, m, el, obj;
		for ( ; m = mutations[ i ]; ++i ) {
			for ( j = 0; el = m.addedNodes[ j ]; ++j ) {
				obj = el.nodeType === 1 && list_elemName[ el.dataset[ "jqueryElement" ] ];
				if ( obj ) {
					initElement( obj, el );
				}
			}
		}
	}).observe( document, {
		subtree: true,
		childList: true
	});
}

$.element = function( obj ) {

	// We add a new entry for all the future elements with the name: `obj.name`.
	// `list_elemName` is use in the MutationObserver.
	list_elemName[ obj.name ] = obj;

	// Set the CSS only one time directly in the <head>.
	if ( obj.css ) {
		obj.style = $( "<style>" )
			.html( obj.css )
			.appendTo( "head" )
		;
	}

	var
		sel = "[data-jquery-element='" + obj.name + "']",
		// Get all the elements who are already in the HTML.
		jqElems = $( sel )
	;

	if ( jqElems.length ) {

		// If we found several elements already in the HTML
		// it's mean the JS files are put at the end of the <body>...
		jqElems.each( init );
	} else {

		// ...Else, it's mean the JS files are in the <head> so, we have
		// to wait for the DOM become ready to not make a conflict with any initialisation.
		$( function() {
			$( sel ).each( init );
		});
	}

	function init() {
		initElement( obj, this );
	}
};

$.fn.element = function( fnName ) {

	// Return directly the jqueryElementObject for this kind of code:
	// var value = $( "#thisOne" ).element().getValue();
	if ( !arguments.length ) {
		return this[ 0 ] && this[ 0 ].jqueryElementObject;
	}

	// Removing the name's methode of the arguments list.
	var args = arraySlice.call( arguments, 1 );

	// The `fn` methode will be called to each jquery-element, example of use:
	// $( ".allTheseOnes" ).element( "methode", argA, argB, ... );
	return this.each( function() {
		var
			proto = this.jqueryElementObject,
			fn = proto && proto[ fnName ]
		;
		if ( fn ) {
			fn.apply( proto, args );
		}
	});
};

})( jQuery );