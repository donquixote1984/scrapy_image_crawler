    $(document).ready(function(){
    var spider_list = $("#spider-list>ul")
    $.getJSON("/client/list_spiders/",function(data){
      $.each(data,function(key, value){ 
        var spider_name = key
        var instance_list = value 

        var spider_name_div = $("<li><a href='#'>"+spider_name+"</a></li>")
        var spider_status_div = $("<span class='spider_status,"+get_status(instance_list)+"'></span>")
        spider_name_div.append(spider_status_div)
        var spider_instance_div = $("<ul class='spider_instance_list'></ul>")
        $.each(instance_list,function(i,data){
            var spider_instance_div_li =$("<li><a href='#'>inst"+(i+1)+"</a></li>")
            status = _get_status(data)
            if(status == "run"){
              spider_instance_div_li.find("a").addClass("spider_running")
            }
            else if(status =="hang"){
              spider_instance_div_li.find("a").addClass("spider_hang")
            }
            else{
              spider_instance_div_li.find("a").addClass("spider_finished")
            }
            spider_instance_div.append(spider_instance_div_li)
            spider_instance_div_li.find("a").click(function(){
              var instance_id = data.instance_id 
              render(spider_name,instance_id) 
            })
        }) 
        spider_name_div.append(spider_instance_div)
        spider_list.append(spider_name_div)

      })
    })
});
  function get_status(instance_list){
    spider_status = []
    prev_sta = null
    $.each(instance_list,function(i,status){
      var sta = _get_status(status)
      if(prev_sta!=null&&prev_sta!=sta){
        return "chaos"
      }
      pre_sta = sta
    })
    return pre_sta
  }

  function _get_status(status){
    if(status.finish_time!=null){
      return "stop"
    }
    if(status.latest_time!=null){
      var time = Date.parse(status.latest_time)
      if(time==null||time==undefined){
        return "stop" 
      }
      else{
        var _time = (new Date()).getTime()
        var delta_in_sec = (_time - time)/1000
        if(delta_in_sec<60){
          return "run"
        }
        else{
          return "hang"
        }
      }
    }
    return "stop"
  }
  function render(spider,instance_id){
    var spider_monitor = $("#spider-monitor-content")    
    var key = spider+":status:"+instance_id
    //var chart = new Chart()
    //chart.spider_key = key
    $.getJSON("/client/list_instance/",{"key":key+":latest"},function(data){
      var current = Date.parse(data.status_time)
      var start_time = current
      if(data.start_time !=null || data.start_time!=undefined){
        start_time = Date.parse(data.start_time)
      }
      var delta = (current-start_time)/1000
      if(data["image_status_count/downloaded"]==null)
        data["image_status_count/downloaded"]=0
      var crawl_v = Math.floor(data["image_status_count/downloaded"]/delta)

      var download_v= Math.floor(data["downloader/response_bytes"]/1024/delta)
      var upload_v = Math.floor(data["downloader/request_bytes"]/1024/delta)
      var start_time_label = data.start_time
      var status_time_label = data.status_time
      var enqueue_size= data["scheduler/enqueued/redis"]
      var dequeue_size = data["scheduler/dequeued/redis"] 
      var velocity_div = $("<div id='velocity'><div class='kpi_title'>Velocity</div><div class='kpi_value'>"+crawl_v+"</div></div>")
      spider_monitor.find("div").remove()
      spider_monitor.append(velocity_div)
    })
  }
