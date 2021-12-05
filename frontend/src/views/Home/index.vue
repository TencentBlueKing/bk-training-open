<template>
    <contentWapper :pageid="pageId" :minheight="pageMinHeight">
        <div class="addReport-body">
            <div class="top_container">
                <div class="fun-bar">
                    <div class="fun-item">
                        <span style="line-height: 32px;">选择模板：</span>
                        <bk-select :disabled="!writeFalg" v-model="curTemplateId"
                            class="select-template"
                            ext-cls="select-custom"
                            ext-popover-cls="select-popover-custom"
                            z-index="99"
                            searchable
                            @selected="selectTemplate()"
                            @change="changeTemplate()"
                            placeholder="请选择模板"
                        >
                            <bk-option v-for="template in templateList"
                                :key="template.id"
                                :id="template.id"
                                :name="template.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="fun-item">
                        <span>选择日期：</span>
                        <bk-date-picker class="mr15" v-model="reportDate"
                            :clearable="false"
                            :placeholder="'选择日期'"
                            :ext-popover-cls="'custom-popover-cls'"
                            :options="customOption"
                            @change="getDailyByDate(reportDate)"
                        >
                        </bk-date-picker>
                    </div>
                    <bk-button :theme="'primary'"
                        :disabled="!writeFalg"
                        type="submit" :title="'保存'" @click="clickSaveDaily()">
                        保存
                    </bk-button>
                    <bk-button style="margin-left:14px;" :theme="'primary'"
                        type="submit" :title="'请假'" @click="leaveManage()">
                        请假
                    </bk-button>
                    <bk-sideslider width="600"
                        :is-show.sync="leaveSetting.visible"
                        :quick-close="false"
                        @hidden="hiddenSlider"
                        ext-cls="leave-slide">
                        <div slot="header" class="slide-header">
                            <div :class="{
                                'header-tabs': true,
                                'tabs-active': tindex === activeTabIndex
                            }" v-for="(title,tindex) in slideTitleList" :key="tindex" @click="changeTab(tindex)">
                                {{title}}
                            </div>
                        </div>
                        <div slot="content">
                            <div class="leave-body" style="height: 530px;padding: 30px 0 0 10px;" v-show="activeTabIndex === 0">
                                <div class="leave-apply">
                                    <bk-form :label-width="80" form-type="horizontal">
                                        <bk-form-item label="请假日期" :required="true">
                                            <bk-date-picker
                                                v-model="leaveFormData.dateTimeRange"
                                                class="mr15"
                                                :clearable="false"
                                                :placeholder="'选择日期范围'"
                                                :type="'daterange'"
                                                @clear="clearDate"
                                            ></bk-date-picker>
                                        </bk-form-item>
                                        <bk-form-item label="请假原因">
                                            <bk-input
                                                placeholder=""
                                                :type="'textarea'"
                                                :rows="3"
                                                :maxlength="255"
                                                v-model="leaveFormData.reason">
                                            </bk-input>
                                        </bk-form-item>
                                        <bk-form-item class="mt20">
                                            <bk-button
                                                style="margin-right: 3px;"
                                                theme="primary" title="提交"
                                                @click.stop.prevent="submitLeave">提交</bk-button>
                                        </bk-form-item>
                                    </bk-form>
                                </div>
                            </div>
                            <div class="leave-body" style="padding: 30px 10px 0;" v-show="activeTabIndex === 1">
                                <div class="leave-manage">
                                    <div class="select-bar">
                                        <div class="ptitle">选择组</div>
                                        <bk-select :disabled="false" v-model="selectedGroup" style="width: 200px;"
                                            ext-cls="select-custom"
                                            ext-popover-cls="select-popover-custom"
                                            @selected="handleSelectGroup"
                                            searchable>
                                            <bk-option v-for="goption in groupList"
                                                :key="goption.id"
                                                :id="goption.id"
                                                :name="goption.name">
                                            </bk-option>
                                        </bk-select>
                                    </div>
                                    <div class="leave-load" v-show="isleaveTableLoad" v-bkloading="{ isLoading: isleaveTableLoad, theme: 'primary', zIndex: 10 }"></div>
                                    <bk-table
                                        v-show="!isleaveTableLoad"
                                        :virtual-render="false"
                                        :data="leaveTableData.data"
                                        :size="leaveTableData.size"
                                        :outer-border="false"
                                        :header-border="false"
                                        :header-cell-style="{ background: '#fff' }"
                                        :pagination="leaveTableData.pagination"
                                        @page-change="handlePageChange"
                                        @page-limit-change="handlePageLimitChange">
                                        <div slot="empty-text">
                                            空数据
                                        </div>
                                        <bk-table-column label="人员信息" prop="name" min-width="150" show-overflow-tooltip="true"></bk-table-column>
                                        <bk-table-column label="请假时间" prop="leaveDate" min-width="180" show-overflow-tooltip="true"></bk-table-column>
                                        <bk-table-column label="请假理由" prop="reason" show-overflow-tooltip="true" min-width="150"></bk-table-column>
                                        <bk-table-column label="操作" width="80">
                                            <template slot-scope="props">
                                                <bk-button class="mr10" theme="primary" text :disabled="!leaveTableData.isAdmin" @click="cancelLeave(props.row)">销假</bk-button>
                                            </template>
                                        </bk-table-column>
                                    </bk-table>
                                </div>
                            </div>
                        </div>
                    </bk-sideslider>
                    
                </div>
                
                <div class="state-bar" style="justify-content: flex-end;">
                    <bk-dialog v-model="saveDailyDialog.visiable" theme="primary" class="save-daily-dialog" :show-footer="false">
                        <bk-form label-width="80">
                            <bk-form-item style="margin-left:60px;">
                                请选择保存方式
                            </bk-form-item>
                            <bk-form-item>
                                <bk-button style="margin-right: 20px;" theme="primary" title="保存并发送邮件" @click.stop.prevent="saveAndSend()">保存并发送邮件</bk-button>
                                <bk-button ext-cls="mr5" @click="saveDaily()" theme="default" title="仅保存">仅保存</bk-button>
                            </bk-form-item>
                        </bk-form>
                    </bk-dialog>
                    <span class="state-text">
                        日报状态：{{saveText}}
                    </span>
                </div>
            </div>

            <div v-show="reportIsLoading" class="test-dom" v-bkloading="{ isLoading: basicLoading, theme: 'primary', zIndex: 10 }">
            </div>
            <!-- 写日报模块 -->
            <div v-show="!reportIsLoading" class="body-container">
                <div v-for="(title,index) in curTemplate" :key="index" style="margin:50px 0px;">
                    <div style="font-size: 18px;font-weight: 700;">{{title}}</div>
                    <div class="input-demo">
                        <bk-input
                            placeholder=""
                            :type="'textarea'"
                            :rows="3"
                            :maxlength="255"
                            v-model="dailyData[index]"
                            :disabled="!writeFalg"
                            @change="saveFalg = true"
                        >
                        </bk-input>
                    </div>
                </div>
            </div>
        </div>
    </contentWapper>

</template>

<script>
    import { bkInput, bkDatePicker, bkTable, bkTableColumn, bkButton, bkSideslider, bkForm, bkFormItem } from 'bk-magic-vue'
    import contentWapper from '../components/content-wapper.vue'

    export default {
        name: '',
        components: {
            contentWapper,
            bkInput,
            bkDatePicker,
            bkTable,
            bkTableColumn,
            bkButton,
            bkSideslider,
            bkForm,
            bkFormItem
        },
        data () {
            return {
                pageId: 'addReport',
                pageMinHeight: 840,
                reportIsLoading: true,
                basicLoading: true,
                templateList: [],
                curTemplateId: null,
                curTemplate: [],
                // 日报内容
                dailyData: [],
                // 添加日报提交表单内容
                addDailyFormData: {
                    date: null,
                    content: {},
                    template_id: null,
                    send_email: false
                },
                reportDate: new Date(),
                checkLeaveDate: new Date(),
                customOption: {
                    disabledDate: function (date) {
                        if (date > new Date()) {
                            return true
                        }
                    }
                },
                saveDailyDialog: {
                    visiable: false
                },
                saveFalg: false,
                writeFalg: true,
                saveText: '未保存',
                clearFlag: 0,
                leaveSetting: {
                    visible: false
                },
                isleaveTableLoad: true,
                leaveTableData: {
                    size: 'small',
                    data: [],
                    isAdmin: false,
                    pagination: {
                        current: 1,
                        count: 0,
                        limit: 10,
                        'limit-list': [10, 20, 50]
                    }
                },
                leaveFormData: {
                    reason: '',
                    dateTimeRange: [new Date(), new Date()]
                },
                slideTitleList: [
                    '请假申请',
                    '请假管理'
                ],
                activeTabIndex: 0, // 0是请假申请 1是请假管理
                groupList: [],
                selectedGroup: ''
            }
        },
        created () {
            const vm = this
            vm.init()
        },
        methods: {
            // 打开请假管理
            leaveManage () {
                this.leaveSetting.visible = true
            },
            // 获取请假管理表
            getLeaveList (type) {
                this.isleaveTableLoad = true
                this.leaveTableData.data = []
                const todayDate = this.formateDate(new Date())
                const groupId = this.selectedGroup
                const sign = 0 // 1 返回未请假人 或 0 返回请假人
                if (type === 1) {
                    this.leaveTableData.pagination.current = (this.leaveTableData.pagination.count - 1) / this.leaveTableData.pagination.limit
                }
                this.$http.get('/display_personnel_information/' + groupId
                    + '/?date=' + todayDate
                    + '&sign=' + sign
                    + '&current_page=' + this.leaveTableData.pagination.current
                    + '&page_size=' + this.leaveTableData.pagination.limit
                ).then(res => {
                    if (res.data.is_admin !== null && res.data.is_admin !== undefined) {
                        this.leaveTableData.isAdmin = res.data.is_admin
                    }
                    if (res.data.total_record !== 0) {
                        this.leaveTableData.pagination.count = res.data.total_record
                        
                        res.data.off_day_list.map((item, index) => {
                            this.leaveTableData.data.push({
                                'offdayId': item.id,
                                'leaveDate': item.start_date + '  ~  ' + item.end_date,
                                'reason': item.reason,
                                'name': item.user + '(' + item.name + ')'
                            })
                        })
                    }
                }).finally(() => {
                    this.isleaveTableLoad = false
                })
            },
            // 请假滑窗关闭事件
            hiddenSlider () {
                this.leaveFormData.reason = ''
                this.leaveFormData.dateTimeRange = [new Date(), new Date()]
                this.activeTabIndex = 0
            },
            // 切换请假页签事件
            changeTab (index) {
                this.activeTabIndex = index
                if (this.activeTabIndex === 1) {
                    this.getLeaveList()
                }
            },
            // 选择组
            handleSelectGroup (value, option) {
                this.getLeaveList()
            },
            // 清空请假日期
            clearDate () {
                this.leaveFormData.dateTimeRange = -1
                console.log('this.leaveFormData.dateTimeRange == ', this.leaveFormData.dateTimeRange)
            },
            // 请假确认事件
            submitLeave () {
                const params = {}
                params.start_date = this.formateDate(this.leaveFormData.dateTimeRange[0])
                params.end_date = this.formateDate(this.leaveFormData.dateTimeRange[1])
                params.reason = this.leaveFormData.reason
                this.$http.post('/add_off_info/', params).then(res => {
                    console.log('dsdsadd = ', res)
                    if (res.result) {
                        console.log('请假成功')
                        console.log('dsdsadd = ', res.result)
                        this.$bkMessage({
                            'offsetY': 80,
                            'delay': 2000,
                            'theme': 'success',
                            'message': res.message
                        })
                    } else {
                        this.$bkMessage({
                            'offsetY': 80,
                            'delay': 2000,
                            'theme': 'warning',
                            'message': res.message
                        })
                    }
                })
            },
            handlePageChange (page) {
                this.leaveTableData.pagination.current = page
                this.getLeaveList()
            },
            handlePageLimitChange () {
                this.leaveTableData.pagination.limit = arguments[0]
                this.getLeaveList()
            },
            cancelLeave (row) {
                console.log(this.leaveTableData.pagination.current)

                const offdayId = row.offdayId
                this.$http.delete('/remove_off/' + this.selectedGroup + '/' + offdayId + '/').then(res => {
                    if (res.result) {
                        this.getLeaveList(1)
                    } else {
                        // 调用获取日报模板接口失败
                        this.$bkMessage({
                            'offsetY': 80,
                            'theme': 'error',
                            'message': res.message
                        })
                    }
                })
            },
            // 转化日期格式yyyy-MM-dd
            formateDate (date) {
                return date.getFullYear() + '-' + (date.getMonth() >= 9 ? (date.getMonth() + 1) : '0' + (date.getMonth() + 1)) + '-' + (date.getDate() > 9 ? (date.getDate()) : '0' + (date.getDate()))
            },
            changeTemplate () {
                console.log(this.curTemplateId + 'x')
                if (this.curTemplateId === null || this.curTemplateId === '') {
                    this.curTemplate = []
                    this.dailyData = []
                }
            },
            // 切换模板
            selectTemplate () {
                this.dailyData = []
                const vm = this
                vm.templateList.forEach(function (template) {
                    if (template.id === vm.curTemplateId) {
                        vm.curTemplate = template.content.split(';')
                    }
                })
            },
            // 界面初始化
            init () {
                const vm = this
                // 开始loading
                vm.reportIsLoading = true
                
                this.$http.get('/get_all_report_template/').then(res => {
                    if (res.result) {
                        this.templateList = res.data
                        this.clearFlag = 1
                        // 获取用户今日的日报
                        this.getDailyByDate(this.reportDate)
                    } else {
                        // 调用获取日报模板接口失败
                        vm.reportIsLoading = false
                        const config = {}
                        config.offsetY = 80
                        config.message = res.message
                        config.theme = 'error'
                        this.$bkMessage(config)
                    }
                })

                // 获取当前用户组信息
                vm.$http.get('/get_user_groups/').then((res) => {
                    console.log('init_group, groupsData:', res.data)
                    vm.groupList = res.data
                    if (vm.groupList.length !== 0) {
                        vm.selectedGroup = vm.groupList[0].id
                    }
                })
            },
            clickSaveDaily () {
                console.log('isToday', this.formateDate(this.reportDate) === this.formateDate(new Date()))
                if (this.formateDate(this.reportDate) === this.formateDate(new Date())) {
                    this.saveDaily()
                } else {
                    this.saveDailyDialog.visiable = true
                }
            },
            // 获取用户指定日期日报，如果没有写日报，则自动渲染第一个模板的内容
            getDailyByDate (date) {
                const vm = this
                this.writeFalg = true
                const config = {}
                config.offsetY = 80
                console.log('templates', this.templateList)
                this.$http.get('/daily_report/?date=' + this.formateDate(date))
                    .then(res => {
                        if (res.result) {
                            console.log('vm.reportIsLoading == ', vm.reportIsLoading)
                            console.log('daily', res.data)
                            if (JSON.stringify(res.data) === '{}') {
                                // 今天的日志还没写
                                if (this.templateList.length > 0) {
                                    // 默认选择第一个默认模板
                                    this.curTemplateId = this.templateList[0].id
                                    this.curTemplate = this.templateList[0].content.split(';')
                                    console.log('curTemplateId:', this.curTemplateId)
                                    console.log('curTemplate', this.curTemplate)
                                    this.dailyData = []
                                    this.saveText = '未保存'
                                }
                            } else {
                                // 写了日报，给日报注入内容
                                const templateContent = []
                                const daily = []
                                for (const key in res.data.content) {
                                    templateContent.push(key)
                                    daily.push(res.data.content[key])
                                }
                                this.curTemplateId = res.data.template_id
                                this.curTemplate = templateContent
                                this.dailyData = daily
                                console.log('curTemplateId', this.curTemplateId)
                                console.log('curTemplate', this.curTemplate)
                                console.log('dailyData', this.dailyData)
                                if (res.data.send_describe === '已发送') {
                                    this.writeFalg = false
                                }
                                this.saveText = res.data.send_describe
                            }
                        } else {
                            // 调用获取当前日报接口失败
                            vm.reportIsLoading = false
                            config.message = res.message
                            config.theme = 'error'
                            this.$bkMessage(config)
                        }
                    }).finally(() => {
                        vm.reportIsLoading = false
                    })
            },
            saveAndSend () {
                this.addDailyFormData.send_email = true
                this.saveDaily()
            },
            // 保存日报
            saveDaily () {
                // 消息提示框的参数设置
                const config = {
                    'offsetY': 80
                }
                if (this.dailyData.length === 0) {
                    config.message = '未填写内容不可以保存日报'
                    config.theme = 'error'
                    this.$bkMessage(config)
                    return
                }
                console.log(this.dailyData)
                let flag = true
                const content = {}
                for (let i = 0; i < this.curTemplate.length; i++) {
                    console.log('日报内容', this.dailyData[i])
                    if (this.dailyData[i] === null || this.dailyData[i] === '' || this.dailyData[i] === undefined) {
                        config.message = '"' + this.curTemplate[i] + '"不可为空'
                        flag = false
                    } else {
                        // 设置日期内容
                        content[this.curTemplate[i]] = this.dailyData[i]
                    }
                }
                console.log('hasFullContentFlag:', flag)
                if (flag === false) {
                    this.addDailyFormData = { date: null, content: {}, template_id: null }
                    config.theme = 'error'
                    this.$bkMessage(config)
                } else {
                    // 设置日期数据
                    this.addDailyFormData.date = this.formateDate(this.reportDate)
                    this.addDailyFormData.content = content
                    this.addDailyFormData.template_id = this.curTemplateId
                    // 调取添加日报接口
                    console.log('addDailyFormData:', this.addDailyFormData)
                    this.$http.post('/daily_report/', this.addDailyFormData).then(res => {
                        config.message = res.message
                        if (res.result) {
                            config.theme = 'success'
                            this.$bkMessage(config)
                            console.log('填写成功，重新获取日报信息')
                        } else {
                            this.addDailyFormData = null
                            config.theme = 'error'
                            this.$bkMessage(config)
                        }
                        this.getDailyByDate(this.reportDate)
                        this.saveDailyDialog.visiable = false
                        this.sendEmail = false
                    })
                }
            }

        }
    }
</script>

<style scoped>
    .test-dom {
        height: 300px;
        line-height: 300px;
        /* border: 1px solid #eee; */
        text-align: center;
    }
    .container-title {
        font-size: 22px;
        font-weight: 700;
    }
    .body-container {
        margin-top:40px;
    }
    .top_container{
        width: 100%;
        display: flex;
        flex-wrap: wrap;
        flex-wrap: wrap;
        justify-content: space-between;
    }
    .top_container /deep/ .bk-date-picker{
        width: 50%;
        position: relative;
        width: 110px;
    }
    .fun-bar{
        width: 700px;
        display: flex;
        justify-content: flex-start;
        flex-flow: wrap;
        flex-direction: row;
    }
    .fun-item{
        display: flex;
        height: 32px;
        line-height: 32px;
        margin-right: 20px;
    }
    .state-bar{
        display: flex;
        height: 32px;
        line-height: 32px;
    }
    .mr15 /deep/ .bk-date-picker-dropdown{
        top:32px !important;
    }
    .input-demo {
        margin-top:20px ;
    }
    .select-template{
        width: 12%;
        min-width: 100px;
        display: inline-block;
        vertical-align: bottom;
    }
    .state-text{
        margin-top: 8px;
        font-size: 16px;
    }
    .leave-slide .slide-header{
        display: flex;
        flex-wrap: nowrap;
    }
    .leave-slide .slide-header .title{
        height: 60px;
        line-height: 60px;
        border-bottom: 1px solid #dcdee5;
        font-size: 16px;
        font-weight: 700;
        color: #666;
    }
    .leave-slide .slide-header .header-tabs{
        width: 50%;
        text-align:center
    }
    .leave-slide .slide-header .tabs-active{
        border-bottom: 2px solid #3a84ff;
        color: #3a84ff;
    }
    .leave-slide .slide-header .header-tabs:hover{
        cursor: pointer;
        color: #3a84ff;
    }
    .leave-slide .leave-manage .leave-load {
        height: 300px;
        line-height: 300px;
        /* border: 1px solid #eee; */
        text-align: center;
    }
    .leave-slide .leave-manage .select-bar{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        margin-bottom: 20px;
    }
    .leave-slide .leave-manage .select-bar .ptitle{
        font-size: 14px;
        font-weight: 400;
        color: #63656e;
        margin-right: 10px;
    }
    .leave-slide .leave-manage .loadbox{
        height: 300px;
        line-height: 300px;
        border: 1px solid #eee;
        text-align: center;
    }
    .leave-slide .leave-body .leave-apply .bk-form .bk-form-item .bk-form-content .bk-form-control{
        width: 94% !important;
    }
    .leave-slide .leave-body .leave-apply .bk-form .bk-form-item .bk-form-content .bk-date-picker{
        width: 200px;
    }
</style>
