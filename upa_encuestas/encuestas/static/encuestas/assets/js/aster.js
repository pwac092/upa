
function chunkString(str, size) {
      var numChunks = Math.ceil(str.length / size),
          chunks = new Array(numChunks);

        for(var i = 0, o = 0; i < numChunks; ++i, o += size) {
                chunks[i] = str.substr(o, size);
                  }

        return chunks.join('<br>');
}

var width = 200,
    height = 200,
    radius = Math.min(width, height) / 2,
    innerRadius = 0.3 * radius;

var pie = d3.layout.pie()
    .sort(null)
    .value(function(d) { return 1; });

var tip = d3.tip()
  .attr('class', 'd3-tip')
  .offset([0, 0])
  .html(function(d) {
    return chunkString(d.data.label,45) + ": <span style='color:orangered'>" + d.data.score.toFixed(2) + "</span>";
  });

var arc = d3.svg.arc()
  .innerRadius(innerRadius)
  .outerRadius(function (d) { 
    return (radius - innerRadius) * (d.data.score / 10.0) + innerRadius; 
  });

var outlineArc = d3.svg.arc()
        .innerRadius(innerRadius)
        .outerRadius(radius);

var svg = d3.select("#aster").append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

svg.call(tip);

var data = {{ csv|safe }};

  data.forEach(function(d) {
    d.score  = +d.score;
    d.label  =  d.label;
    d.id     =  d.id;
    d.color  =  d.color;
  });

  var path = svg.selectAll(".solidArc")
      .data(pie(data))
    .enter().append("path")
      .attr("fill", function(d) { return d.data.color; })
      .attr("class", "solidArc")
      .attr("stroke", "gray")
      .attr("d", arc)
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide);

  var outerPath = svg.selectAll(".outlineArc")
      .data(pie(data))
    .enter().append("path")
      .attr("fill", "none")
      .attr("stroke", "gray")
      .attr("class", "outlineArc")
      .attr("d", outlineArc);  


  // calculate the weighted mean score
var score =                                              
   data.reduce(function(a, b) {                           
             //console.log('a:' + a + ', b.score: ' + b.score + ', b.weight: ' + b.weight);
             return a + (b.score * b.weight);                     
                 }, 0) /  
    data.reduce(function(a, b) {                           
          return a + b.weight;  
  }, 0);

  svg.append("svg:text")
    .attr("class", "aster-score")
    .attr("dy", ".35em")
    .attr("text-anchor", "middle") // text-align: right
    .text(Math.round(score));

//for the autcomplete of the students.
var availableTags = {{students|safe}};
$("#students").autocomplete({
    source: availableTags,
    response: function( event, ui ) {
        $("#validStudents").empty();
        for (var i = 0; i < ui.content.length; i++) {
            console.log(ui.content[i].value);
            $("#validStudents").append("<p>"+ui.content[i].value+"</p>");
        }
    },
    open: function( event, ui ) {
        $(".ui-autocomplete").hide();
    }
});
