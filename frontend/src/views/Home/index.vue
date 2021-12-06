<template>
    <div class="body">
        <div class="container">
            <div class="top_container">
                <span style="display: inline-block;margin-left:50px;">选择日期：</span>
                <bk-date-picker class="mr15" v-model="reportDate"
                    :clearable="false"
                    :placeholder="'选择日期'"
                    :ext-popover-cls="'custom-popover-cls'"
                    :options="customOption"
                    @change="changeDate(reportDate)"
                >
                </bk-date-picker>
                <div>
                    <h2 class="mr30 f20" style="margin: 0;">
                        日报状态：
                        <span v-if="hasWrittenToday" style="color: #3A84FF;font-size: 18px;">已写日报</span>
                        <span v-else style="color: #63656E;font-size: 18px;">未写日报</span>
                    </h2>
                </div>
                <div>
                    <span class="mr10 f20">隐私模式</span>
                    <bk-switcher size="large" v-model="dailyData.isPrivate" class="mr30"></bk-switcher>
                </div>
                <bk-button :theme="'primary'" style="display: inline-block" @click="saveDaily" class="mr30">
                    保存
                </bk-button>
                <bk-button :theme="'primary'" style="display: inline-block" @click="leaveManage" class="mr30">
                    请假
                </bk-button>
                <bk-sideslider width="600"
                    :is-show.sync="leaveSetting.visible"
                    :quick-close="true"
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
                                    @page-change="handlePageChange"
                                    @page-limit-change="handlePageLimitChange">
                                    <div slot="empty-text">
                                        空数据
                                    </div>
                                    <bk-table-column label="人员信息" prop="info" min-width="150" show-overflow-tooltip="true"></bk-table-column>
                                    <bk-table-column label="请假时间" prop="leaveDate" min-width="180" show-overflow-tooltip="true"></bk-table-column>
                                    <bk-table-column label="请假理由" prop="reason" show-overflow-tooltip="true"></bk-table-column>
                                    <bk-table-column label="操作" width="80">
                                        <template slot-scope="props">
                                            <bk-button class="mr10" theme="primary" text :disabled="currentUserName !== props.row.usernmae" @click="cancelLeave(props.row)">取消</bk-button>
                                        </template>
                                    </bk-table-column>
                                </bk-table>
                            </div>
                        </div>
                    </div>
                </bk-sideslider>
                <bk-button :theme="'success'" style="display: inline-block" @click="moreTemplateDialog.visible = true">
                    添加模板
                </bk-button>
            </div>
            <div class="bottom_container">
                <template v-for="(title, index) in dailyData.title">
                    <div :key="index">
                        <div style="display: flex;justify-content: space-between;margin: 10px 0">
                            <h2 contenteditable="true" @input="changeTitleText(index)" :ref="'title' + index" style="display: inline-block;margin: 0">{{title}}</h2>
                            <bk-button style="display: inline-block" :theme="'primary'" @click="dealAdd(index)">
                                新增一条内容
                            </bk-button>
                        </div>
                        <div>
                            <bk-table
                                style="margin-top: 15px;"
                                :data="dailyData.content[index]"
                                :virtual-render="true"
                                height="175px">
                                <bk-table-column prop="content" label="内容"></bk-table-column>
                                <bk-table-column width="150" prop="cost" label="所花时间"></bk-table-column>
                                <bk-table-column label="操作" width="150">
                                    <template slot-scope="props">
                                        <bk-button
                                            theme="warning"
                                            text
                                            @click="changeContent(props.row, index)">
                                            修改
                                        </bk-button>
                                        <bk-button
                                            theme="danger"
                                            text
                                            @click="deleteContent(props.row, index)">
                                            删除
                                        </bk-button>
                                    </template>
                                </bk-table-column>
                            </bk-table>
                        </div>
                    </div>
                </template>
                <bk-dialog
                    v-model="addDialog.visible"
                    title="新增内容"
                    :header-position="addDialog.headerPosition"
                    :width="addDialog.width"
                    @value-change="addDialogChange"
                    :position="{ top: 20, left: 100 }">
                    <div>
                        <h3>内容</h3>
                        <bk-input
                            placeholder="新内容"
                            :type="'textarea'"
                            :rows="3"
                            v-model="newContent"
                        >
                        </bk-input>
                        <h3>所花时间</h3>
                        <bk-input
                            placeholder="所花时间"
                            type="number"
                            v-model="newCost"
                            :precision="1"
                            :min="0"
                        >
                            <template slot="append">
                                <div class="group-text">小时</div>
                            </template>
                        </bk-input>
                    </div>
                    <div slot="footer" class="dialog-foot">
                        <div>
                            <bk-button v-if="isAdd" :theme="'primary'" :title="'分享'" @click="addRow">
                                添加
                            </bk-button>
                            <bk-button v-else :theme="'primary'" :title="'分享'" @click="changeRow">
                                修改
                            </bk-button>
                        </div>
                    </div>
                </bk-dialog>
                <bk-dialog
                    v-model="moreTemplateDialog.visible"
                    :header-position="moreTemplateDialog.headerPosition"
                    :width="moreTemplateDialog.width"
                    @value-change="moreTemplateDialogChange"
                    :position="{ top: 20, left: 100 }">
                    <div slot="header">
                        <span class="mr30">新增模板标题</span>
                    </div>
                    <div>
                        <bk-input
                            placeholder="新增模板标题"
                            :type="'text'"
                            v-model="newTitle"
                        >
                        </bk-input>
                    </div>
                    <div slot="footer" class="dialog-foot">
                        <div>
                            <bk-button :theme="'primary'" :title="'分享'" @click="addTemplate">
                                添加
                            </bk-button>
                        </div>
                    </div>
                </bk-dialog>
            </div>
            <template v-for="(tem,index) in dailyTemplates">
                <div :key="index">
                    <div style="display: flex;justify-content: space-between;margin: 10px 0">
                        <h2 style="display: inline-block;margin: 0">{{tem}}</h2>
                        <bk-button v-if="index > 0" style="display: inline-block" :theme="'primary'" @click="deleteTemplate(index)">
                            删除该模板
                        </bk-button>
                    </div>
                    <bk-input
                        placeholder="请输入"
                        :type="'textarea'"
                        :rows="3"
                        v-model="templateContent[index]"
                    >
                    </bk-input>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    export default {
        data () {
            return {
                curDate: new Date(),
                formatDate: '',
                addDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                // 此次操作是增加一列还是修改一列
                isAdd: true,
                // 修改指定行的临时变量
                targetRow: 0,
                moreTemplateDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                // 日报信息
                dailyData: {
                    title: ['今日任务', '明日计划'],
                    content: [[], []],
                    isPrivate: false
                },
                dailyDates: [],
                // 新的内容和新花费时间的临时变量
                newContent: '',
                newCost: 0,
                // 指向dailyData.content的下标
                currentIndex: 0,
                // 提交数据的格式化对象
                postDaily: {
                    date: null,
                    content: {},
                    template_id: 0,
                    send_email: false,
                    isPrivate: 0
                },
                // 新的模板标题及内容数组
                dailyTemplates: ['感想'],
                templateContent: [],
                // 新标题临时变量
                newTitle: '',
                // 今日写日报状况（已写，未写）
                hasWrittenToday: false,
                customOption: {
                    disabledDate: function (date) {
                        if (date > new Date()) {
                            return true
                        }
                    }
                },
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
                selectedGroup: '',
                currentUserName: ''
            }
        },
        created () {
            this.formatDate = moment(new Date()).format(moment.HTML5_FMT.DATE)
            const dateInURL = this.$route.query.date
            if (dateInURL !== undefined) {
                this.reportDate = new Date(dateInURL)
                this.formatDate = dateInURL
            } else {
                this.reportDate = new Date()
            }
            this.init()
        },
        methods: {
            changeDate (date) {
                this.formatDate = moment(date).format(moment.HTML5_FMT.DATE)
                this.getDailyReport()
            },
            cheakDailyDates () {
                this.$http.get('/get_reports_dates/').then(res => {
                    if (res.result) {
                        this.dailyDates = res.data
                        this.customOption = {
                            disabledDate: (date) => {
                                if (this.dailyDates.includes(moment(date).format('YYYY-MM-DD')) || this.curDate < date) {
                                    return true
                                }
                            }
                        }
                    } else {
                        this.$bkMessage({
                            offsetY: 80,
                            message: res.message,
                            theme: 'error'
                        })
                    }
                })
            },
            changeTemplate () {
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
                this.cheakDailyDates()
                this.getDailyReport()
                const vm = this
                // 获取当前用户组信息
                vm.$http.get('/get_user_groups/').then((res) => {
                    console.log('init_group, groupsData:', res.data)
                    vm.groupList = res.data
                    if (vm.groupList.length !== 0) {
                        vm.selectedGroup = vm.groupList[0].id
                    }
                })
            },
            getDailyReport () {
                this.$http.get(
                    '/daily_report/?date=' + this.formatDate
                ).then(res => {
                    this.cheakDailyDates()
                    if (Object.keys(res.data).length) {
                        this.hasWrittenToday = true
                    } else {
                        this.hasWrittenToday = false
                    }
                })
            },
            // 改变默认模板标题
            changeTitleText (index) {
                const title = 'title' + index
                this.dailyData.title[index] = this.$refs[title][0].innerText
            },
            // 打开dialog, 增加一行
            dealAdd (index) {
                this.currentIndex = index
                this.isAdd = true
                this.addDialog.visible = true
            },
            // 保存增加表格中的一行新内容
            addRow () {
                const newObj = { 'content': this.newContent, 'cost': this.newCost + '小时' }
                this.dailyData.content[this.currentIndex].push(newObj)
                this.addDialog.visible = false
            },
            // 保存对指定行的修改
            changeRow () {
                const newObj = { 'content': this.newContent, 'cost': this.newCost + '小时' }
                this.dailyData.content[this.currentIndex].splice(this.targetRow, 1, newObj)
                this.addDialog.visible = false
            },
            // 打开dailog,改变表格中指定行内容
            changeContent (row, changeIndex) {
                this.currentIndex = changeIndex
                this.newContent = row.content
                this.newCost = parseFloat(row.cost)
                this.targetRow = row.$index
                this.isAdd = false
                this.addDialog.visible = true
            },
            // 删除表格中的一行内容
            deleteContent (row, removeIndex) {
                this.dailyData.content[removeIndex].splice(row.$index, 1)
                this.$bkMessage({
                    theme: 'success',
                    message: '移除成功'
                })
            },
            // 保存日报
            saveDaily () {
                this.postDaily.date = this.formatDate
                for (const index in this.dailyData.content) {
                    this.postDaily.content[this.dailyData.title[index]] = this.dailyData.content[index]
                }
                for (const index in this.templateContent) {
                    this.postDaily.content[this.dailyTemplates[index]] = this.templateContent[index]
                }
                this.postDaily.content['isPrivate'] = this.dailyData.isPrivate
                this.$http.post(
                    '/daily_report/', this.postDaily
                ).then(res => {
                    this.hasWrittenToday = true
                    this.$bkMessage({
                        theme: 'success',
                        message: res.message
                    })
                })
            },
            // 增加自定义模板标题
            addTemplate () {
                this.dailyTemplates.push(this.newTitle)
                this.moreTemplateDialog.visible = false
            },
            // 删除自定义模板标题
            deleteTemplate (index) {
                this.dailyTemplates.splice(index, 1)
            },
            addDialogChange (val) {
                if (val === false) {
                    this.newContent = ''
                    this.newCost = 0
                }
            },
            moreTemplateDialogChange (val) {
                if (val === false) {
                    this.newTitle = ''
                }
            },
            // 转化日期格式yyyy-MM-dd
            formateDate (date) {
                return date.getFullYear() + '-' + (date.getMonth() >= 9 ? (date.getMonth() + 1) : '0' + (date.getMonth() + 1)) + '-' + (date.getDate() > 9 ? (date.getDate()) : '0' + (date.getDate()))
            },
            // 打开请假管理
            leaveManage () {
                this.leaveSetting.visible = true
            },
            // 获取请假管理表
            getLeaveList () {
                this.isleaveTableLoad = true
                this.leaveTableData.data = []
                const todayDate = this.formateDate(new Date())
                const groupId = this.selectedGroup
                const sign = 0 // 1 返回未请假人 或 0 返回请假人
                this.$http.get('/display_personnel_information/' + groupId
                    + '/?date=' + todayDate
                    + '&sign=' + sign
                ).then(res => {
                    if (res.data.off_day_list !== undefined) {
                        res.data.off_day_list.map((item, index) => {
                            this.leaveTableData.data.push({
                                'offdayId': item.id,
                                'leaveDate': item.start_date + '  ~  ' + item.end_date,
                                'reason': item.reason,
                                'info': item.user + '(' + item.name + ')',
                                'usernmae': item.user
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
                    if (res.result) {
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
            // 取消假期事件
            cancelLeave (row) {
                const offdayId = row.offdayId
                this.$http.delete('/remove_off/' + this.selectedGroup + '/' + offdayId + '/').then(res => {
                    if (res.result) {
                        this.getLeaveList()
                    } else {
                        this.$bkMessage({
                            'offsetY': 80,
                            'theme': 'warning',
                            'message': res.message
                        })
                    }
                })
            }
        }
    }
</script>

<style scoped>
.body{
    border: 2px solid #EAEBF0 ;
    margin:0px 100px;
    padding: 20px 50px;
    min-height: 80vh;
}
.container_title {
    font-size: 22px;
    font-weight: 700;
}
.top_container{
    width: 100%;
    padding: 10px 0;
    display: flex;
    justify-content: flex-end;
}
.bottom_container{
    width: 100%;
    padding-top: 20px;
}
::-webkit-scrollbar{
    display: none;
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
