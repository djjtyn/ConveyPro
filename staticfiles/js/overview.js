//This file contains JS relevant to the overview page
$(document).ready(() => {
    initDonutCharts();
});

function initDonutCharts() {
    const amountPerStageTrackerObj = createAmountsPerStageObj()
    const totalAmount = Number($('#opportunityCount').text());
    renderSmallDonuts(totalAmount);
    $('#largeDonutGraph').append(renderLargeDonut(amountPerStageTrackerObj));
}

function createAmountsPerStageObj() {
    const amountPerStageTracker = {
        'For Sale': $('#forSaleStageCount').text(),
        'Sale Agreed': $('#saleAgreedstageCount').text(), 
        'Contracts Exchanged':  $('#contractsExchangedStageCount').text(),
        'Sold': $('#soldStageCount').text()
    }
    return amountPerStageTracker;
}

function renderSmallDonuts(totalAmount){
    // Get each stage count
    const stages = document.querySelectorAll('.propertyStageCount h3');
    stages.forEach((element) => {
        const stageCount = Number(element.querySelector('span:not(.stageName)').innerText);
        const stageName = element.querySelector('.stageName').innerText.trim();
        let canvas;
        let bgColor;
        //Create canvas element
        if (stageName == 'For Sale') {
            canvas = document.getElementById('forSaleDonut');
            bgColor = 'orange';
        }
        if (stageName == 'Sale Agreed') {
            canvas = document.getElementById('saleAgreedDonut');
            bgColor = '#A654F0';
        }
        if (stageName == 'Contracts Exchanged') {
            canvas = document.getElementById('contractsExchangedDonut');
            bgColor = '#FF4AA0';
        }
        if (stageName == 'Sold') {
            canvas = document.getElementById('soldDonut');
            bgColor = 'limegreen';
        }
        let renderAmount = stageCount > 0? totalAmount - stageCount:totalAmount;
        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: [stageName, 'Other'],
                datasets: [{
                    data: [stageCount, renderAmount],
                    backgroundColor: [
                        bgColor,
                        '#e6e6e6'
                    ]
                }]
            }
        })
    })
}

function renderLargeDonut(amountPerStageTracker) {
    const data = createStageObjItemArray(amountPerStageTracker)
    const width = $('#largeDonutGraph').width();
    const height = width/2;

    // Create the color scale.
    const color = d3.scaleOrdinal()
      .domain(data.map(d => d.label))
      .range(d3.schemeCategory10)

  // Create the pie layout and arc generator.
  const pie = d3.pie()
      .sort(null)
      .value(d => d.value);

  const arc = d3.arc()
      .innerRadius(0)
      .outerRadius(Math.min(width, height) / 2 - 1);

  const labelRadius = arc.outerRadius()() * 0.8;

  // A separate arc generator for labels.
  const arcLabel = d3.arc()
      .innerRadius(labelRadius)
      .outerRadius(labelRadius);

  const arcs = pie(data);

  // Create the SVG container.
  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [-width / 2, -height / 2, width, height])
      .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

  // Add a sector path for each value.
  svg.append("g")
      .attr("stroke", "white")
    .selectAll()
    .data(arcs)
    .join("path")
      .attr("fill", d => color(d.data.label))
      .attr("d", arc)
    .append("title")
      .text(d => `${d.data.label}: ${d.data.value.toLocaleString("en-US")}`);

  // Create a new arc generator to place a label close to the edge.
  // The label shows the value if there is enough room.
  svg.append("g")
      .attr("text-anchor", "middle")
    .selectAll()
    .data(arcs)
    .join("text")
      .attr("transform", d => `translate(${arcLabel.centroid(d)})`)
      .call(text => text.append("tspan")
          .attr("y", "-0.4em")
          .attr("font-weight", "bold")
          .text(d => d.data.label))
      .call(text => text.filter(d => (d.endAngle - d.startAngle) > 0.25).append("tspan")
          .attr("x", 0)
          .attr("y", "0.7em")
          .attr("fill-opacity", 0.7)
          .text(d => d.data.value.toLocaleString("en-US")));

  return svg.node();
}

function createStageObjItemArray(amountPerStageTracker){
//Create an object for each item in amountPerStageTracker and append it to data array
    const data = [];
    Object.keys(amountPerStageTracker).forEach(key => {
        const value = amountPerStageTracker[key];
        if(value > 0) {
            const obj = {
                'label': key,
                'value': amountPerStageTracker[key]
            }
            data.push(obj)
        }
    });
    return data;
}



