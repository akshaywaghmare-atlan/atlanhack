var u=Object.defineProperty;var p=(n,t,e)=>t in n?u(n,t,{enumerable:!0,configurable:!0,writable:!0,value:e}):n[t]=e;var o=(n,t,e)=>p(n,typeof t!="symbol"?t+"":t,e);import{i as g,F as b,f as x,a as f,R as m}from"./B4mcmQk5.js";function v(n,t){let e=null;return function(...a){const i=this;e!==null&&clearTimeout(e),e=setTimeout(()=>{n.apply(i,a),e=null},t)}}class y{constructor(t,e){o(this,"container");o(this,"columns");o(this,"data");o(this,"options");o(this,"searchTerm","");o(this,"dateRange","Last 1 hour");o(this,"startDate",null);o(this,"endDate",null);o(this,"expandedGroups",new Set);o(this,"filterData",async(t,e)=>{const a=await this.options.onChange({key:t,value:e}),i=this.container.querySelector("#tableBody");i.innerHTML=this.renderTableRows(a);const r=this.container.querySelector("#searchInput");r&&(r.value=this.searchTerm)});this.container=document.getElementById(t),this.columns=e.columns,this.data=e.data,this.options=e.options,this.render(),this.attachEventListeners()}getInputStyles(){return`
            width: 100%;
            padding: 6px 12px;
            border: 1px solid rgb(224, 228, 235);
            background-color: #fff;
            outline: #3c72df;
            color: rgb(75, 85, 99);
            border-radius: 4px;
            font-size: 1rem;
            line-height: 1.2;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        `}render(){this.container.innerHTML=`
        <div class="bg-white text-slate-900 p-4 flex flex-col h-full">
            ${this.options.searchable?`<div class="flex justify-between items-center mb-4 w-full bg-white py-4">
                    <div class="flex-grow relative mr-2">
                        <input type="text" placeholder="Search logs..." style="${this.getInputStyles()}" class="focus:outline-blue-500 focus:border-blue-400 focus:border-solid focus:border-1 hover:border hover:border-solid hover:border-blue-400" id="searchInput">
                        <button id="clearSearch" class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 bg-transparent hover:text-gray-600 focus:outline-none">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    <div class="flex-shrink-0">
                        <button type="button" class="inline-flex justify-center w-full rounded-md shadow-sm px-4 py-2 bg-blue-500 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500" id="dateRangeButton">
                            <span id="dateRangeText">Last 1 hour</span>
                            <svg class="-mr-1 ml-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                        </button>
                        <div class="hidden origin-top-right absolute right-7 z-10 mt-2 w-56 rounded-md shadow-lg bg-white text-slate-800 ring-1 ring-black ring-opacity-5 divide-y divide-gray-700" id="dateRangeDropdown">
                            <div class="py-1">
                                <a href="#" class="block px-4 py-2 text-sm text-slate-900 hover:bg-blue-500 hover:text-white" data-range="Last 5 minutes">Last 5 minutes</a>
                                <a href="#" class="block px-4 py-2 text-sm text-slate-900 hover:bg-blue-500 hover:text-white" data-range="Last 15 minutes">Last 15 minutes</a>
                                <a href="#" class="block px-4 py-2 text-sm text-slate-900 hover:bg-blue-500 hover:text-white" data-range="Last 30 minutes">Last 30 minutes</a>
                                <a href="#" class="block px-4 py-2 text-sm text-slate-900 hover:bg-blue-500 hover:text-white" data-range="Last 1 hour">Last 1 hour</a>
                                <a href="#" class="block px-4 py-2 text-sm text-slate-900 hover:bg-blue-500 hover:text-white" data-range="Last 3 hours">Last 3 hours</a>
                                <a href="#" class="block px-4 py-2 text-sm text-slate-900 hover:bg-blue-500 hover:text-white" data-range="Last 6 hours">Last 6 hours</a>
                                <a href="#" class="block px-4 py-2 text-sm text-slate-900 hover:bg-blue-500 hover:text-white" data-range="Last 12 hours">Last 12 hours</a>
                                <a href="#" class="block px-4 py-2 text-sm text-slate-900 hover:bg-blue-500 hover:text-white" data-range="Last 24 hours">Last 24 hours</a>
                                <a href="#" class="block px-4 py-2 text-sm text-slate-900 hover:bg-blue-500 hover:text-white" data-range="Last 2 days">Last 2 days</a>
                                <a href="#" class="block px-4 py-2 text-sm text-slate-900 hover:bg-blue-500 hover:text-white" data-range="custom">Custom Range</a>
                            </div>
                            <div class="py-1">
                                <div class="px-4 py-2">
                                    <div class="flex flex-col space-y-2">
                                        <label for="startDate" class="text-sm font-medium text-gray-900">Start Date</label>
                                        <input type="datetime-local" id="startDate" class="text-slate-700 bg-white px-2 py-1 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 border border-blue-500 border-solid pl-10">
                                    </div>
                                    <div class="flex flex-col space-y-2 mt-2">
                                        <label for="endDate" class="text-sm font-medium text-gray-900">End Date</label>
                                        <input type="datetime-local" id="endDate" class="text-slate-700 bg-white px-2 py-1 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 border border-blue-500 border-solid pl-10">
                                    </div>
                                    <button id="applyDateRange" class="mt-4 w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800">Apply</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`:""}

            <div class="flex-grow overflow-hidden">
                <div class="overflow-x-auto">
                    <div class="inline-block min-w-full align-middle">
                        <div class="overflow-hidden shadow-sm">
                            <div class="max-h-[calc(100vh-72px)] overflow-y-auto">
                                <table class="min-w-full divide-y divide-gray-200">
                                    <thead class="bg-gray-50">
                                        <tr>
                                            ${this.options.expandable?'<th scope="col" class="px-4 py-2 text-left text-base bold text-gray-900 tracking-wider sticky top-0 bg-slate-100 rounded-md font-semibold"></th>':""}
                                            ${this.columns.map(t=>`
                                                <th scope="col" class="px-4 py-2 text-left text-base bold text-gray-900 tracking-wider sticky top-0 bg-slate-100 rounded-mdfont-semibold">
                                                    <div class="flex items-center">
                                                        ${t.header}
                                                    </div>
                                                </th>
                                            `).join("")}
                                        </tr>
                                    </thead>
                                    <tbody class="bg-white divide-y divide-gray-200" id="tableBody">
                                        ${this.renderTableRows(this.data)}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `}renderTableRows(t){return(t||this.data).map((a,i)=>{const r=this.expandedGroups.has(a.trace_id);return`
                <tr class="hover:bg-blue-50 text-base font-normal">
                    ${this.options.expandable?`
                        <td class="px-2 py-1">
                            <button class="expand-button p-1 rounded-full bg-slate-200 hover:bg-slate-300 text-slate-600" data-index="${i}" data-trace-id="${a.trace_id}">
                                <svg class="w-4 h-4 transform transition-transform duration-200 ${r?"rotate-90":""}" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                                </svg>
                            </button>
                        </td>
                    `:""}
                    ${this.columns.map(s=>`
                        <td class="${typeof s.formatter=="function"?"p-0":"px-4 py-2"} whitespace-nowrap text-base text-gray-900">
                            ${this.renderCell(a,s)}
                        </td>
                    `).join("")}
                </tr>
                ${r?this.renderSpans(a.spans,a.trace_id):""}
            `}).join("")}renderSpans(t,e){return t.map(a=>`
            <tr class="bg-gray-50" data-parent-trace-id="${e}">
                <td colspan="${this.columns.length+(this.options.expandable?1:0)}" class="px-4 py-2">
                    <div class="pl-8">
                        <div class="flex flex-row flex-wrap">
                            <div class="ml-6 mr-2"><span class="text-base mr-2">Span ID:</span> ${a.span_id}</div>
                            <div class="basis-1/4"><span class="text-base mr-2">Name:</span> ${a.name}</div>
                            <div class="basis-1/4"><span class="text-base mr-2">Start Time:</span> ${new Date(a.start_time).toLocaleString()}</div>
                            <div class="basis-1/4"><span class="text-base mr-2">End Time:</span> ${new Date(a.end_time).toLocaleString()}</div>
                        </div>
                    </div>
                </td>
            </tr>
        `).join("")}renderCell(t,e){return e.formatter?e.formatter(t[e.key]):t[e.key]}clearSearch(){const t=this.container.querySelector("#searchInput");console.log(t.value,"<-- searchInput.value"),t.value?this.filterData("search",""):(t.value="",this.searchTerm="")}attachEventListeners(){const t=this.container.querySelector("#searchInput"),e=this.container.querySelector("#clearSearch"),a=v(this.handleSearch.bind(this),300);t.addEventListener("input",s=>{a(s)}),e.addEventListener("click",this.clearSearch.bind(this)),this.container.querySelector("#dateRangeButton").addEventListener("click",this.toggleDateRangeDropdown.bind(this)),this.container.querySelectorAll("#dateRangeDropdown a").forEach(s=>{s.addEventListener("click",this.handleDateRangeSelection.bind(this))}),this.container.querySelector("#applyDateRange").addEventListener("click",this.handleCustomDateRange.bind(this)),this.options.scrollable&&this.container.querySelector("#tableBody").addEventListener("scroll",this.handleScroll.bind(this)),this.options.expandable&&this.container.querySelector("#tableBody").addEventListener("click",d=>{const h=d.target.closest(".expand-button");if(h){const c=h.getAttribute("data-trace-id");c&&(this.expandedGroups.has(c)?this.expandedGroups.delete(c):this.expandedGroups.add(c),this.updateExpandedRow(c))}})}updateExpandedRow(t){var a;const e=(a=this.container.querySelector(`button[data-trace-id="${t}"]`))==null?void 0:a.closest("tr");if(e){const i=this.expandedGroups.has(t),r=e.querySelector(".expand-button svg");r&&r.classList.toggle("rotate-90",i);const l=this.container.querySelectorAll(`tr[data-parent-trace-id="${t}"]`);if(i)if(l.length===0){const s=this.data.find(d=>d.trace_id===t);if(s){const d=this.renderSpans(s.spans,t);e.insertAdjacentHTML("afterend",d)}}else l.forEach(s=>s.classList.remove("hidden"));else l.forEach(s=>s.classList.add("hidden"))}}handleSearch(t){this.searchTerm=t.target.value,console.log(this.searchTerm,"this.searchTerm"),this.filterData("search",this.searchTerm)}toggleDateRangeDropdown(){this.container.querySelector("#dateRangeDropdown").classList.toggle("hidden")}handleCustomDateRange(){const t=this.container.querySelector("#startDate"),e=this.container.querySelector("#endDate");this.startDate=t.value?new Date(t.value):null,this.endDate=e.value?new Date(e.value):null,this.startDate&&this.endDate?(this.dateRange="Custom",this.updateDateRangeText(),this.toggleDateRangeDropdown(),console.log(this.startDate,this.endDate,"<-- handleCustomDateRange"),this.filterData("customDate",{startDate:this.startDate,endDate:this.endDate})):alert("Please select both start and end dates.")}updateDateRangeText(){const t=this.container.querySelector("#dateRangeText");if(this.dateRange==="Custom"&&this.startDate&&this.endDate){const e=a=>a.toLocaleString("en-US",{year:"numeric",month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"});t.textContent=`${e(this.startDate)} - ${e(this.endDate)}`}else t.textContent=this.dateRange}handleDateRangeSelection(t){t.preventDefault();const a=t.target.getAttribute("data-range");a&&(this.dateRange=a,this.startDate=null,this.endDate=null,this.updateDateRangeText(),this.toggleDateRangeDropdown(),this.filterData("daterange",a))}handleScroll(t){const e=t.target;e.scrollHeight-e.scrollTop===e.clientHeight&&console.log("Fetching more data...")}}class w{constructor(t){o(this,"chart",null);o(this,"options");this.options=t,this.initChart()}initChart(){const t=document.getElementById(this.options.container);if(!t){console.error(`Container with id "${this.options.container}" not found`);return}this.chart=g(t),this.updateChart()}getChartOption(){const t={title:this.options.title?{text:this.options.title}:void 0,tooltip:{trigger:"axis",axisPointer:{type:"cross",label:{backgroundColor:"#6a7985"}}},legend:{data:this.options.series.map(e=>e.name)},toolbox:{feature:{saveAsImage:{}}},grid:{left:"3%",right:"4%",bottom:"3%",containLabel:!0},xAxis:{type:"category",boundaryGap:!1,data:this.options.xAxis.data,name:this.options.xAxis.name},yAxis:{type:"value",name:this.options.yAxis.name},series:this.options.series.map(e=>({name:e.name,type:e.type,data:e.data,smooth:e.smooth!==void 0?e.smooth:!0,areaStyle:void 0}))};return this.options.color&&(t.color=this.options.color),this.options.type==="histogram"&&(t.series=[{type:"bar",data:this.options.series[0].data,barWidth:"99.3%"}],t.xAxis.boundaryGap=!0),t}updateChart(t){var a;t&&(this.options={...this.options,...t});const e=this.getChartOption();(a=this.chart)==null||a.setOption(e)}resize(){var t;(t=this.chart)==null||t.resize()}destroy(){var t;(t=this.chart)==null||t.dispose()}}const R={FormBuilder:b,formConfig:x,api:f,RenderUI:m,Table:y,BaseChart:w};export{R as s};
