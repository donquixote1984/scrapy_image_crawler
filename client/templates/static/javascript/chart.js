function Chart(){
    this.data_arr=[]
    this.length=50
    this.key = ""
    this.options= {}
    this.line = null
    this.push_data =function(current,data){
        if(this.data_arr.length>this.length){
            this.data_arr.shift()
        }
        var chart_data = {
                    name:new Date(current).format("HH:mm:ss"),
                    value:data,
                    line_width:1,
                    color:'#0d8ecf'
                }
       this.data_arr.push(chart_data) 
    }
    this.init_options = function(){
        this.options.render="status-chart"
        this.options.data = this.data_arr
        this.options.border=0
        this.options.title="Spider instance velocity"
        this.options.width=800
        this.options.height=200
        this.options.align='center'
        this.options.tip={
                                enable:true,
                                style:"border:1px solid #ddd;background:#eee;padding:3px;box-shadow:0 0 3px #222 inset",
                                listeners:{
                                    parseText:function(tip,name,value,text,i){
                                    return "<div><div><span style='text-align:center;font-weight:bold;font-size:14pt'>"+value+"</span><span style='font-family:Bubbler One,sans-serif'>  d/s</span></div><div style='color:#111;font-family:Bubbler One,sans-serif'>"+name+"</div></div>"

                        }
                    }
                            }
        this.options.crosshair={
                                enable:true,
                                line_color:'#62bce9'
                            }
        this.options.sub_option = {
                    smooth : true,
                    label:false,
                    point_size:7
                }
        

        labels=[]
        for(var i=0;i<1;i++){
            labels.push('')
        }

        this.options.labels= labels

        this.options.coordinate={
                    width:640,
                    height:260,
                    striped_factor : 0.18,
                    grid_color:'#efefef',
                    axis:{
                        color:'#eee',
                        width:[0,0,2,2]
                    },
                    scale:[{
                         position:'left',   
                         start_scale:0,
                         end_scale:50,
                         scale_space:10,
                         scale_size:2,
                         scale_enable : false,
                         label : {color:'#9d987a',font : '微软雅黑',fontsize:11,fontweight:600},
                         scale_color:'#9f9f9f'
                    },{
                         position:'bottom', 
                         label : {color:'#9d987a',font : '微软雅黑',fontsize:11,fontweight:600},
                         scale_enable : false,
                         labels:labels
                    }]
                }

        this.line = new iChart.Column2D(this.options) 
        /*this.line = new iChart.LineBasic2D({
                        render : 'status-chart',
                        data: [{value:[1,2,3,4,5]}],
                        title : '北京2012年平均温度情况',
                        width : 800,
                        height : 400,
                        coordinate:{height:'90%',background_color:'#f6f9fa'},
                        sub_option:{
                            hollow_inside:false,//设置一个点的亮色在外环的效果
                            point_size:16
                        },
                        labels:["一月","二月","三月","四月","五月","六月","七月","八月","九月","十月","十一月","十二月"]
                    
        })*/
        var chart_inst = this
        $.getJSON("/client/list_instance_status/",{"key":this.key+":list","size":this.length},function(data){
            $.each(data, function(i,item){
                var current = Date.parse(item.status_time)
                var start_time = current
                if(item.start_time !=null || item.start_time!=undefined){
                    start_time = Date.parse(item.start_time)
                } 
                if(item["image_status_count/downloaded"]!=null){
                var delta = (current-start_time)/1000
                var crawl_v = delta!=0? Math.floor(item["image_status_count/downloaded"]/delta):0 
                chart_inst.push_data(current,crawl_v)}
            })
            chart_inst.line.load(chart_inst.data_arr)
        })
    }
    
    this.clear = function(){
        this.data_arr = []
    }
    this.draw= function(){
        var chart_inst = this
      //  setInterval(this.draw_segment,2000)        
      chart_inst.line.load(chart_inst.data_arr)
    }
}


 Date.prototype.format = function(mask) {  
   
     var d = this;  
   
     var zeroize = function (value, length) {  
   
         if (!length) length = 2;  
   
         value = String(value);  
   
         for (var i = 0, zeros = ''; i < (length - value.length); i++) {  
   
             zeros += '0';  
   
         }  
   
         return zeros + value;  
   
     };    
   
     return mask.replace(/"[^"]*"|'[^']*'|\b(?:d{1,4}|m{1,4}|M{1,4}|yy(?:yy)?|([hHMstT])\1?|[lLZ])\b/g, function($0) { 
   
         switch($0) {  
   
             case 'd':   return d.getDate();  
   
             case 'dd':  return zeroize(d.getDate());  
   
             case 'ddd': return ['Sun','Mon','Tue','Wed','Thr','Fri','Sat'][d.getDay()];  
   
             case 'dddd':    return ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][d.getDay()];  
   
             case 'M':   return d.getMonth() + 1;  
   
             case 'MM':  return zeroize(d.getMonth() + 1);  
   
             case 'MMM': return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getMonth()];  
   
             case 'MMMM':
             return ['January','February','March','April','May','June','July','August','September','October','November','December'][d.getMonth()];  
   
             case 'yy':  return String(d.getFullYear()).substr(2);  
   
             case 'yyyy':    return d.getFullYear();  
   
             case 'h':   return d.getHours() % 12 || 12;  
   
             case 'hh':  return zeroize(d.getHours() % 12 || 12);  
   
             case 'H':   return d.getHours();  
   
             case 'HH':  return zeroize(d.getHours());  
   
             case 'm':   return d.getMinutes();  
   
             case 'mm':  return zeroize(d.getMinutes());  
   
             case 's':   return d.getSeconds();  
   
             case 'ss':  return zeroize(d.getSeconds());  
   
             case 'l':   return zeroize(d.getMilliseconds(), 3);  
   
             case 'L':   var m = d.getMilliseconds();  
   
                     if (m > 99) m = Math.round(m / 10);  
   
                     return zeroize(m);  
   
             case 'tt':  
                    return d.getHours() < 12 ? 'am' : 'pm';  
                
             case 'TT':  return d.getHours() < 12 ? 'AM' : 'PM';  
   
             case 'Z':   return d.toUTCString().match(/[A-Z]+$/);  
   
             // Return quoted strings with the surrounding quotes removed  
   
             default:    return $0.substr(1, $0.length - 2);  
   
         }  
   
     });  
   
 };  