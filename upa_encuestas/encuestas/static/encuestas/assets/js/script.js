
// Get pre-computed histogram data

function breaklines(str, n) {
    var lines = str.split(/\s+/), // explode on whitespaces
        n = +n || 50;
    var res = [];
    for (var i=0; i<lines.length; ) {
        for (var l = 0, line = []; l + lines[i].length <= n; i++) {
            l += 1 + lines[i].length;
            line.push(lines[i]);
        }
        res.push(line.join(" "));
    }
    return res.join("<br>");
}

d3.json("data.json", function(json) {

  

  var maxBin = 4;

  var binInc = 1;

  for( var i = 0; i < json.length; i++) {

    // use the name of the group to initialize the array

    var group = json[i].name;

    var data = [];

    

    // we have a max bin for our histogram, must ensure

    // that any bins > maximum bin are rolled into the 

    // last bin that we have

    var binCounts = {};

    for( var j = 0; j < json[i].data.length; j++) {

      var xValue = json[i].data[j].bin;

      // bin cannot exceed the maximum bin

      xValue = ( xValue > maxBin ? maxBin : xValue);

      var yValue = json[i].data[j].count;

      

      if(binCounts[xValue] === undefined) {

        binCounts[xValue] = 0;

      }

      binCounts[xValue] += yValue;

    }

    

    // add the bin counts in

    for( var bin in binCounts) {

      data.push({"x": bin, "y": binCounts[bin]});

    }

    

    // add the histogram
    //var line = breaklines(group.toUpperCase(),10)
    var line = group.toUpperCase();


    createHistogram(data, maxBin, binInc,line) 

  }

});

var createHistogram = function(data, maxBin, binInc, title) {


  // A formatter for counts.

  var formatCount = d3.format(",.0f");

  var totalWidth = 380;

  var totalHeight = 240;

  var margin = {top: 40, right: 60, bottom: 50, left: 70},

      width = totalWidth - margin.left - margin.right,

      height = totalHeight - margin.top - margin.bottom;

  

  var binArray = [];

  for (var i = 0; i <= maxBin + binInc; i += binInc) {

    binArray.push(i);

  }

  var binTicks = [];

  for (var i = 0; i < maxBin + binInc; i += binInc) {

    binTicks.push(i);

  }

  

  var x = d3.scale.linear()

      .domain([0, maxBin + binInc])

      .range([0, width]);

  var binWidth = parseFloat(width / (binArray.length - 1)) - 1;

  

  var y = d3.scale.linear()

      .domain([0, d3.max(data, function(d) { return d.y; })])

      .range([height, 0]);

  

  var xAxis = d3.svg.axis()

      .scale(x)

      .orient("bottom")

      .tickValues(binTicks);

      

  var yAxis = d3.svg.axis()

      .scale(y)

      .orient("left");

  

  var svg = d3.select("body").append("svg")

      .attr("width", width + margin.left + margin.right)

      .attr("height", height + margin.top + margin.bottom)

      .append("g")

      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  

  var bar = svg.selectAll(".bar")

      .data(data)

      .enter()

      .append("rect")

      .attr("class", "bar")

      .attr("x", function(d) { return x(d.x); })

      .attr("width", binWidth)

      .attr("y", function(d) { return y(d.y); })

      .attr("height", function(d) { return height - y(d.y); })

      .on("mouseover", function(d) {

        var barWidth = parseFloat(d3.select(this).attr("width"));

        var xPosition = parseFloat(d3.select(this).attr("x")) + (barWidth / 2);

        var yPosition = parseFloat(d3.select(this).attr("y")) - 10;

        

        svg.append("text")

          .attr("id", "tooltip")

          .attr("x", xPosition)

          .attr("y", yPosition)

          .attr("text-anchor", "middle")

          .text(d.y);

      })

      .on("mouseout", function(d) {

        d3.select('#tooltip').remove();

      });

  

  svg.append("g")

      .attr("class", "x axis")

      .attr("transform", "translate(0," + height + ")")

      .call(xAxis);

      

  svg.append("g")

      .attr("class", "y axis")

      //.attr("transform", "translate(0," + height + ")")

      .call(yAxis);

      

  // Add axis labels

  svg.append("text")

      .attr("class", "x label")

      .attr("transform", "translate(" + (width / 2) + " ," + (height + margin.bottom - 15) + ")")

      //.attr("dy", "1em")

      .attr("text-anchor", "middle")

      .text("Score ");

      

  svg.append("text")

      .attr("class", "y label")

      .attr("transform", "rotate(-90)")

      .attr("y", 0 - margin.left)

      .attr("x", 0 - (height / 2))

      .attr("dy", "1em")

      .attr("text-anchor", "middle")

      .text("Count");

      

  // Add title to chart

  svg.append("text")

      .attr("class", "title")

      .attr("transform", "translate(" + (width - width) + " ," + (-10) + ")")

      //.attr("dy", "1em")

      .attr("text-anchor", "right")

      .text(title);  

};

                


