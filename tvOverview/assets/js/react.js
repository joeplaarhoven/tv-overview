
jQuery(document).ready(function ($) {
      var value = JSON.parse(localStorage.getItem('startTimer'));
       console.log(value)
   });

//errorList
function update(errorList, thresholdList, hitRate){
  // console.log(errorList)
  // var errors = errorList.sort(function(a, b){
  //   // ASC  -> a.length - b.length
  //   // DESC -> b.length - a.length
  //   return b[1].length - a[1].length;
  // })
  // var deviceName = ''
  // var errorList = []
  // var fullError = []
  //
  // for (var x = 0; x <= 10; x++){
  //   errorList = ''
  //   for(var s in errors[x][1]){
  //     errorList += errors[x][1][s]
  //     errorList += ', '
  //   }
  //   var errorL = errorList.slice(0, -2);
  //   console.log(errorL)
  //   var percentage = errorL.length
  //
  //
  //   var klant = errors[x][0].split('@')
  //   console.log(klant[0])
  //
  //   var device = klant[1].split('.')
  //   console.log(device[0])
  //   var errorRow = '<tr id=t'+t+' style="background-color: rgba(255, 0, 0, 0.'+Math.round(percentage)+')"><td>' + device[0] + '</td><td>' + klant[0] + '</td><td>' + errorL + '</td></tr>'
  //   fullError.push(errorRow)
  // }
  //
  // $( "#error" ).html( fullError );


  //threshold
  var fullThreshold = []

  var threshold = thresholdList.sort(sortFunction);

  function sortFunction(a, b) {
      if (a[1] === b[1]) {
          return 0;
      }
      else {
          return (a[1] < b[1]) ? -1 : 1;
      }
  }
  for (var t = 0; t <= 10; t++){
    errorList = ''
    var percentage = threshold[t][1] / threshold[t][2] * 100
    var klant = threshold[t][0].split('@')

    var device = klant[1].split('.')

    var thresholdRow = '<tr id=t'+t+' style="background-color: rgba(255, 0, 0, 0.'+Math.round(percentage)+')"><td>' + device[0] + '</td><td>' + klant[0] + '</td><td>' + threshold[t][1] + '</td><td>' + threshold[t][2] + '</td></tr>'

    fullThreshold.push(thresholdRow)
  }

  $( "#threshold" ).html( fullThreshold );





  var hitRateList = []

  var hitRate = hitRate.sort(sortFunction);

  function sortFunction(a, b) {
      if (a[1] === b[1]) {
          return 0;
      }
      else {
          return (a[1] > b[1]) ? -1 : 1;
      }
  }

  // Hitrate
  for (var h = 0; h <= 10; h++){
    errorList = ''
    var klant = hitRate[h][0].split('@')


    var device = klant[1].split('.')
    console.log(device, klant)


    var hitRateRow = '<tr id=t'+t+' ><td>' + device[0] + '</td><td>' + klant[0] + '</td><td>' + hitRate[h][1] + '</td></tr>'

    hitRateList.push(hitRateRow)
  }
  $( "#hitRate" ).html( hitRateList );

  var options = {
    chart: {
      animations: {
        enabled: false
      },
      width: 450,
      type: 'donut',
      },
      dataLabels: {
        enabled: true
      },
      labels: ['no problem', '0 scans', 'Under threshold'],
      colors:['#36d94f', '#d93636', '#d97021'],
      series: chartdata,
      responsive: [{
          breakpoint: 480,
          options: {
              chart: {
                  width: 400
              },
              legend: {
                  show: false
              }
          }
      }],
      legend: {
          position: 'right',
          offsetY: 0,
          height: 400,
      }
  }

  var chart = new ApexCharts(
      document.querySelector("#matplotlib"),
      options
  );

  chart.render()
}



$( document ).ready(function() {
  update(errorList, thresholdList, hitRate)

});

function arr_diff (a1, a2) {

    var a = [], diff = [];

    for (var i = 0; i < a1.length; i++) {
        a[a1[i]] = true;
    }

    for (var i = 0; i < a2.length; i++) {
        if (a[a2[i]]) {
            delete a[a2[i]];
        } else {
            a[a2[i]] = true;
        }
    }

    for (var k in a) {
        diff.push(k);
    }

    return diff;
}


setInterval(function(){

  var oldErrorList = errorList.sort(function(a, b){
    // ASC  -> a.length - b.length
    // DESC -> b.length - a.length
    return b[1].length - a[1].length;
  })

  $.ajax({
    url: 'update',
    type:'GET',
    dataType: 'json',
    success: function(result){
      var errorList = result['errors']
      var thresholdList = result['threshold']
      var hitRate = result['hitRate']

      update(errorList, thresholdList, hitRate)
    }
  });
}, 30000);
