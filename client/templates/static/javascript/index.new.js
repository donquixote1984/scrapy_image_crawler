
  function _get_status(status){
    if(status.finish_time!=null){
      return "stop"
    }
    if(status.status_time!=null){
      var time = Date.parse(status.status_time)
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

function RenderPage(){
    this.spiders=null
    this.status=null
    this.requests =null
    this.data=null
    this.selected_instance_data =null
    this.selected_spider_id = null
    this.chart = new Chart()
    this.request_rendered =false 
    this.requests_page = 1
    this.control_container = null
    this.new_spider_control = null
    this.width=window.innerWidth
    this.height=window.innerHeight
    this.renderspiders = function(){
        if(this.data == null){
            return
        }
        var page = this
        page.spiders.find("li").remove()
        $.each(this.data,function(key,value){
            var spider_name = key
            var instance_list = value             
            var spider_name_div = $("<li><a href='#'>"+spider_name+"<span class='spider_fork'></span></a></li>")
            var spider_instance_div = $("<ul class='spider_instance_list'></ul>")
            $.each(instance_list,function(key, value){
                var spider_instance_div_li =$("<li><a href='#'>"+key.substring(0,8)+"</a></li>")
                if(page.selected_instance_id==key)
                    spider_instance_div_li.find("a").addClass("highlight")
                status = value.status 
                spider_instance_div_li.find("a").addClass("spider_"+status)
                spider_instance_div.append(spider_instance_div_li)
                spider_instance_div_li.find("a").click(function(){
                $(this).parent().find("a").removeClass("highlight")
                $(this).addClass("highlight")
                page.selected_instance_id = key
                page.selected_spider_id = spider_name
                    page.chart.clear()
                    page.chart.key = page.selected_spider_id + ":status:"+page.selected_instance_id
                    page.chart.init_options()
                    page.renderstatus() 
                    page.renderrequests()
                })
            })
            spider_name_div.append(spider_instance_div)
            page.spiders.append(spider_name_div)
            spider_name_div.find(".spider_fork").click(function(){
                if(confirm("Ready to run a new crawler?")){
                    $.getJSON("/client/new_crawl/",{"name":spider_name},function(data){
                       if(data.status=="ok"){
                            var modal = $(".crawl_process_modal")
                            var process_bar = $("#crawl_process")
                            process_bar.css({"left":page.width/2,"top":page.height/2})
                                    modal.show()
                            process_bar.find(".bar").animate({"width":"150%"},10000,function(){
                                modal.hide()
                                process_bar.find(".bar").css({"width":"0%"})
                            })
                       } 
                       else{
                        alert(data.message)
                       }
                    }) 
                }
                return false
            })
        })
    }
    this.renderrequests = function(){
        if(this.request_rendered==true)
            return
        if(this.selected_spider_id==null)
            return 
        var page= this
        $.getJSON("/client/list_requests/",{"spider":this.selected_spider_id},function(data){
            $.each(data,function(i,item){
                var url = item.url
                var url_li = $("<li><a href='"+url+"'>"+url+"</a></li>")
                page.requests.append(url_li)
            })
            
            
        })
        page.requests.parent().find(".pagination").click(function(){
            page.requests_page++;
            $.getJSON('/client/list_requests/',{"spider":page.selected_spider_id,"p":page.requests_page},function(data){
                $.each(data,function(i,item){
                    var url = item.url
                    var url_li = $("<li><a href='"+url+"'>"+url+"</a></li>")
                    page.requests.append(url_li)
                })
            })
        })
        this.request_rendered=true
    }
    this.renderstatus = function(){
        if(this.selected_spider_id == null){
          //  alert('null id')
            return
        }

        if(this.selected_instance_id == null){
            alert('null data')
            return
        }
        
        //this.chart.draw()
        this.selected_instance_data = this.data[this.selected_spider_id][this.selected_instance_id]
        var instance_id = this.selected_instance_id
        var instance_data = this.data[this.selected_spider_id][this.selected_instance_id]
        var current = Date.parse(instance_data.status_time)
        var start_time = current
        if(instance_data.start_time !=null || instance_data.start_time!=undefined){
            start_time = Date.parse(instance_data.start_time)
        }
        var delta = (current-start_time)/1000
        var crawl_v = delta!=0? Math.floor(instance_data["image_status_count/downloaded"]/delta):0
        this.chart.push_data(current,crawl_v)
        this.chart.draw()
        var download_v= delta!=0? Math.floor(instance_data["downloader/response_bytes"]/1024/delta):0
        var upload_v = delta!=0? Math.floor(instance_data["downloader/request_bytes"]/1024/delta):0
        var start_time_label = instance_data.start_time
        var status_time_label = instance_data.status_time
        var enqueue_size= instance_data["scheduler/enqueued/redis"]
        var dequeue_size = instance_data["scheduler/dequeued/redis"] 
        $("#velocity_kpi").find(".kpi_value").text(crawl_v+" downloads/second")
        $("#download_kpi").find(".kpi_value").text(download_v+" kb/second")
        $("#upload_kpi").find(".kpi_value").text(upload_v+" kb/second")
        $("#start_time_kpi").find(".kpi_value").text(start_time_label)
        $("#equeue_kpi").find(".kpi_value").text(enqueue_size)
        $("#dequeue_kpi").find(".kpi_value").text(dequeue_size)
        $("#crawled_key_kpi").text(instance_data["image_count"])
        $("#saved_images_kpi").text(instance_data["db/image_saved_count"])
        $("#saved_pages_kpi").find(".kpi_value").text(instance_data["db/page_saved_count"])
        var download_size = instance_data["image_downloaded_size"]*1.0/(1000*1000)
        if(download_size>1000){
            download_size = download_size/1000.0
            download_size.toFixed(1) 
            $("#downloads_key_kpi").text(download_size.toFixed(2)+" G")
        }
        else{
         $("#downloads_key_kpi").text(download_size.toFixed(1)+" M") 
        }
        this.refresh_control() 
    }
    this.refresh_control=function(){
        var run_status = "finished"
        if(this.selected_instance_data.status!=null)
            run_status = this.selected_instance_data.status
        var container = this.control_container 
        var prev_status = container.attr("status")
        if(run_status==prev_status)
            return
        container.attr("class","")
        container.attr("status",status)
        container.addClass("control-"+run_status)


    }
    this.init_control = function(){
        
        var container = $("#test_container")
        var page=this
        container.find("#test_control").click(function(){
            var run_status = ""
            if(page.selected_instance_data!=null)
                run_status =page.selected_instance_data.status

            var status = container.attr("status")
            if (status!=run_status){
                container.attr("status",run_status)
            }
            var button = $(this)
            if(status=="running"){
                //pause
                $.getJSON("/client/interupt_crawl/",{"id":page.selected_instance_id},function(data){
                    if(data.status=="ok"){
                        container.attr("class","")
                        container.addClass("control-stopping")
                        container.attr("status","stopping")
                        page.selected_instance_data.status="stopping"
                    }
                    else{
                        alert(data.message)
                    }
                })
            }
            else if(status=="finished"){
               //resume 
               $.getJSON("/client/resume_crawl/",{"id":page.selected_instance_id},function(data){
                if(data.status=="ok"){
                    container.attr("class","")
                    container.addClass("control-running")
                    container.attr("status","running")
                    page.selected_instance_data.status="running"
                }
                else{
                    alert(data.message)
                }
               })
            }
            else{

            }
        })
      
    }
    this.run = function(){
        var page = this
        $.getJSON("/client/list_spiders/", function(data){
             page.data = data
             page.renderspiders()
             page.renderstatus()

        })
    }

    this.add_new_spider = function(){
        var page = this
        var spider_new_ul =  $("#spider_new_list")
        $(".panel_header_controls").find("a").click(function(){
            spider_new_ul.find("li").remove()
            $.getJSON("/client/list_new_spiders/",function(data){
                
                $.each(data,function(i,value){
                   var spider_new_li  =$("<li><a href='#'>"+value+"</a></li>") 
                   spider_new_ul.append(spider_new_li)
                   spider_new_li.click(function(){
                    var spider_name = spider_new_li.text()
                    $.get("/client/add_spiders/",{"name":spider_name},function(data){
                        //close the shit
                        //and refresh the left panel
                        page.run()
                        $("#myModal").find(".close").click()
                    })
                   })
                })
            })
            $("#myModal").modal()
        })
    }
}

    $(document).ready(function(){
        r = new RenderPage()
        r.spiders = $("#spider-list>ul")
        r.status = $("#status-kpi")
        r.requests =$("#requests_q>ul")
        r.control_container = $("#test_container")
        r.init_control()
        r.run()
        r.add_new_spider()
        setInterval(function(){
            r.run()
        }, 5000)
    })



