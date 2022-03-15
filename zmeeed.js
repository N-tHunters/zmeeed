const vis = require('vis-network')
const spawn = require("child_process").spawn

// These variables will be injected into a page that will use them.
/* eslint no-unused-vars: "off" */

const options = {
    manipulation: false,
    height: "100%",
    interaction: {
        dragNodes: false
    },
    layout: {
        hierarchical: {
            enabled: true
        }
    }
};



var container = document.getElementById("mynetwork");
var data = { nodes: nodes, edges: edges };
var gph = new vis.Network(container, data, options);
