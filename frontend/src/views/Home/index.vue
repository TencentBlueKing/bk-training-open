<template>
    <div class="body">
        <div class="container">
            <div class="top-container">
                <div class="top-container-left">
                    <!-- 日期选择器 -->
                    <div class="top-container-left-picker">
                        <bk-date-picker
                            v-model="formatDate"
                            :clearable="false"
                            placeholder="选择日期"
                            :options="customOption"
                            @change="changeDate"
                            :shortcuts="shortcuts"
                            :shortcut-close="true"
                        >
                        </bk-date-picker>
                    </div>
                    <div>
                        <bk-button class="top-container-right-btn" :hover-theme="'primary'" @click="clickLeaveManage">
                            请假管理
                        </bk-button>
                    </div>
                </div>
                <div class="top-container-right">
                    <div>
                        <Onoff class="allOnoff" :scope="true" @changeState="setAllPrivate"></Onoff>
                    </div>
                    <bk-button :hover-theme="'primary'" class="top-container-right-btn savedaily" style="display: inline-block" @click="saveDaily">
                        {{ hasWrittenToday ? '修改' : '保存' }}
                    </bk-button>
                </div>
            </div>
            <div class="bottom_container">
                <template v-for="(singleContent, index) in renderList.dailyDataContent">
                    <!-- 今日任务 & 日报填写 -->
                    <div style="margin-bottom: 20px" :key="singleContent">
                        <h3 class="top-h3" :ref="'title' + index">{{singleContent.title}}</h3>
                        <div class="single-card-box" v-for="(item,i) in singleContent.content" :key="item.$index">
                            <div class="single-card-header">
                                <bk-input style="margin-top: 10px; width: 50px;" :ref="`numberDom${index}${i}`" type="number" @blur="changeNumber(item,index,i,$event)" v-model="item.cost" placeholder="时间" :show-controls="false"></bk-input>
                                <div class="input-append">h</div>
                                <!-- 隐私框 -->
                                <Onoff class="Onoff" :state="item.isPrivate" @changeState="(val) => {
                                    item.isPrivate = val
                                }"></Onoff>
                                <bk-icon @click="textChange(item,index)" style="position:absolute;top:-8px; right:-8px;cursor: pointer;fontSize:25px" type="close" />
                            </div>
                            <bk-input placeholder="请填写内容" class="content-textarea" :type="'textarea'" :rows="3" :maxlength="255" v-model="item.text"></bk-input>
                        </div>
                        <div class="renderli">
                            <div class="renderli-add-btn" @click="dealAdd(index)">
                                + 添加一条
                            </div>
                        </div>
                    </div>
                </template>
                <template style="margin-bottom: 40px" v-for="(tem,index) in renderList.newTemplateContent">
                    <div :key="index" style="margin-top: 20px">
                        <div class="temp-top">
                            <h3 class="top-h3">
                                {{tem.title}}
                            </h3>
                        </div>
                        <div class="single-card-box temtextarea">
                            <bk-input placeholder="请填写内容" class="content-textarea" :type="'textarea'" :rows="3" :maxlength="255" v-model="tem.text"></bk-input>
                        </div>
                    </div>
                </template>
            </div>
            <!-- 抽屉 -->
            <bk-sideslider
                width="600"
                :is-show.sync=" leaveSetting.visible"
                :quick-close="true"
                @hidden="hiddenSlider"
                direction="right"
                ext-cls="leave-slide">
                <!-- 下部分主题内容 -->
                <div slot="content">
                    <bk-date-picker
                        v-show="activeTabTitle === '请假申请'"
                        v-model="leaveFormData.dateTimeRange"
                        class="slide-header-picker"
                        :clearable="false"
                        placeholder="选择日期范围"
                        type="daterange"
                        :options="customLeaveOption"
                        @clear="clearDate"
                    ></bk-date-picker>
                    <!-- 组选择器 -->
                    <bk-select v-show="activeTabTitle === '请假信息'" :disabled="false" v-model="selectedGroup" style="width: 200px;"
                        class="slide-header-select"
                        ext-popover-cls="select-popover-custom"
                        @selected="handleSelectGroup"
                        searchable>
                        <bk-option v-for="goption in groupList"
                            :key="goption.id"
                            :id="goption.id"
                            :name="goption.name">
                        </bk-option>
                    </bk-select>
                    <div class="bk-button-group">
                        <bk-button @click="changeTab('请假申请')" :class="activeTabTitle === '请假申请' ? 'is-selected' : ''">请假申请</bk-button>
                        <bk-button @click="changeTab('请假信息')" :class="activeTabTitle === '请假信息' ? 'is-selected' : ''">请假信息</bk-button>
                    </div>
                    <!-- 请假申请 -->
                    <div class="leave-body" v-show="activeTabTitle === slideTitleList[0]">
                        <div class="temp-top">
                            <h3 class="top-h3">
                                请假原因
                            </h3>
                        </div>
                        <div class="single-card-box temtextarea leave-body-textarea">
                            <bk-input placeholder="请填写内容" :type="'textarea'" :rows="3" :maxlength="50" v-model="leaveFormData.reason"></bk-input>
                        </div>
                        <bk-button class="leave-body-submit" :hover-theme="'primary'" @click="submitLeave">
                            提交
                        </bk-button>
                    </div>
                    <!-- 请假信息 -->
                    <div class="leave-body" style="padding: 30px 10px 0;" v-show="activeTabTitle === slideTitleList[1]">
                        <div class="leave-manage">
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
                                <bk-table-column label="人员信息" min-width="30">
                                    <template slot-scope="props">
                                        <div>{{props.row.username}}</div>
                                        <div>{{props.row.name}}</div>
                                    </template>
                                </bk-table-column>
                                <bk-table-column label="请假时间" min-width="10">
                                    <template slot-scope="props">
                                        <div>{{props.row.start_date}}</div>
                                        <div>{{props.row.end_date}}</div>
                                    </template>
                                </bk-table-column>
                                <bk-table-column label="请假理由" prop="reason" min-width="200" show-overflow-tooltip="true"></bk-table-column>
                                <bk-table-column label="操作" width="66">
                                    <template slot-scope="props">
                                        <bk-button :disabled="props.row.username !== myMsg.username && !isAdmin" class="mr10" theme="primary" text @click="removeLeave(props.row)">删除</bk-button>
                                    </template>
                                </bk-table-column>
                            </bk-table>
                        </div>
                    </div>
                </div>
            </bk-sideslider>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import {
        bkButton,
        bkDatePicker,
        bkInput,
        bkSideslider,
        bkTable,
        bkTableColumn
    } from 'bk-magic-vue'
    import Onoff from '@/components/Home/Onoff/index.vue'
    import requestApi from '@/api/request.js'
    import { isAdmin } from '@/utils/index.js'
    const { getallGroups, getReportsDates, getYesterday, getAppointDaily, selectPerMsg, applyRest, removeOff, setUpdateDaily } = requestApi
    export default {
        components: {
            bkInput,
            bkDatePicker,
            bkTable,
            bkTableColumn,
            bkButton,
            bkSideslider,
            Onoff
        },
        data () {
            return {
                // 我自己的信息
                myMsg: JSON.parse(window.localStorage.getItem('userMsg')),
                isAdmin: null,
                // 快捷选择日期
                shortcuts: [
                    {
                        text: '今天',
                        value () {
                            return new Date()
                        }
                    }
                ],
                // 日期选择器的日期
                formatDate: moment(new Date()).format(moment.HTML5_FMT.DATE),
                // 模板弹出框的配置项
                moreTemplateDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                // 渲染的数据
                renderList: {
                    // 日报信息
                    dailyDataTitle: ['今日任务', '明日计划'],
                    dailyDataContent: [
                        { 'title': '今日任务', 'type': 'table', 'content': [] },
                        { 'title': '明日计划', 'type': 'table', 'content': [] }
                    ],
                    // 新的模板标题及内容数组
                    newTemplateContent: [
                        { 'title': '感想', 'type': 'text', 'text': '' }
                    ]
                },
                allPrivate: true,
                dailyDates: [],
                // 新标题临时变量
                newTitle: '',
                // 指向dailyData.content的下标
                currentIndex: 0,
                // 提交数据的格式化对象
                newPostDaily: {
                    date: null,
                    content: [],
                    template_id: 0,
                    send_email: false
                },
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
                    isAdmin: false
                },
                leaveFormData: {
                    reason: '',
                    dateTimeRange: [new Date(), new Date()]
                },
                slideTitleList: [
                    '请假申请',
                    '请假信息'
                ],
                activeTabTitle: '请假申请',
                groupList: [],
                selectedGroup: -1,
                customLeaveOption: {
                    disabledDate: function (date) {
                        const nowDate = new Date()
                        if (date < nowDate.setHours(nowDate.getHours() - 24)) {
                            return true
                        }
                    }
                },
                curUserLeaveList: []
            }
        },
        watch: {
            selectedGroup (oldVal) {
                this.isAdmin = isAdmin(this.myMsg.username, this.groupList.filter(item => item.id === oldVal)[0].admin)
            }
        },
        created () {
            if (this.$route.query.date !== undefined) {
                this.formatDate = this.$route.query.date
            }
            this.init()
        },
        activated () {
            // 如果没有加入任何组就跳转到我的小组页面
            getallGroups().then(res => {
                if (res.result) {
                    // 没有加入任何组就跳转到我的小组页面
                    if (res.data.length === 0) {
                        this.$router.push({ name: 'MyGroup' })
                    }
                } else {
                    this.showBkMessage(res.message)
                }
            })
        },
        methods: {
            changeDate (date) {
                this.formatDate = moment(date).format(moment.HTML5_FMT.DATE)
                this.getDailyReport()
            },
            // 获得当前用户哪些日期写了日报
            cheakDailyDates () {
                getReportsDates().then(res => {
                    if (res.result) {
                        // 配置 日期选择器中哪些为灰色
                        this.customOption = {
                            disabledDate: (date) => {
                                if (moment(date).format('YYYY-MM-DD') !== moment(new Date()).format('YYYY-MM-DD') && (res.data.includes(moment(date).format('YYYY-MM-DD')) || date > new Date())) {
                                    return true
                                }
                            }
                        }
                    } else {
                        this.showBkMessage(res.message)
                    }
                })
            },
            changeTemplate () {
                if (this.curTemplateId === null || this.curTemplateId === '') {
                    this.curTemplate = []
                    this.dailyData = []
                }
            },
            // 昨天日报填了没
            checkYesterdayDaliy () {
                getYesterday().then(res => {
                    if (!res.result) {
                        this.showBkMessage('昨天的日报还没写！记得补上哦！', 'warning', 8000)
                    }
                })
            },
            // 界面初始化
            init () {
                this.cheakDailyDates()
                this.getDailyReport()
                // 获取当前用户组信息
                getallGroups().then(res => {
                    if (res.result) {
                        if (res.data.length !== 0 && res.data.length !== null) {
                            this.groupList = res.data
                            if (this.groupList.length !== 0 && this.groupList.length !== undefined) {
                                // 如果有组默认一个  请假模块
                                this.selectedGroup = this.groupList[0].id
                            }
                        } else {
                            this.groupList = []
                            this.$router.push({ name: 'MyGroup' })
                        }
                    } else {
                        this.showBkMessage(res.message)
                    }
                })
                // 看看昨天日报写了没
                this.checkYesterdayDaliy()
            },
            // 设置日报是不是私有的(全局)
            setAllPrivate (val) {
                for (const item of this.renderList.dailyDataContent) {
                    for (const itemContent of item.content) {
                        itemContent.isPrivate = !val
                    }
                }
            },
            // 获得自己指定时间的日报(渲染)
            getDailyReport () {
                getAppointDaily(this.formatDate).then(res => {
                    if (Object.keys(res.data).length) {
                        this.hasWrittenToday = true
                        this.renderList = {
                            dailyDataTitle: [],
                            dailyDataContent: [],
                            newTemplateContent: []
                        }
                        for (const singleContent of res.data.content) {
                            // 根源
                            if (singleContent.type === 'table') {
                                // 今日任务 & 每日计划
                                this.renderList.dailyDataTitle.push(singleContent.title)
                                this.renderList.dailyDataContent.push(singleContent)
                            } else {
                                // 感想
                                this.renderList.newTemplateContent.push(singleContent)
                            }
                        }
                    } else {
                        // 选中日期未填写日报初始化界面
                        this.notFilledRender()
                    }
                })
            },
            // 选中日期未填写日报初始化界面
            notFilledRender () {
                // 初始化数据
                this.hasWrittenToday = false
                this.renderList = {
                    dailyDataTitle: ['今日任务', '明日计划'],
                    dailyDataContent: [
                        { 'title': '今日任务', 'type': 'table', 'content': [{ cost: 0, isPrivate: true }] },
                        { 'title': '明日计划', 'type': 'table', 'content': [{ cost: 0, isPrivate: true }] }
                    ],
                    newTemplateContent: [
                        { 'title': '感想', 'type': 'text', 'text': '' }
                    ]
                }
            },
            // 打开dialog, 增加一行
            dealAdd (index) {
                const contentLength = this.renderList.dailyDataContent[index].content.length
                // 新增一行的条件是 上一行内容不能为空
                if (contentLength && !this.renderList.dailyDataContent[index].content[contentLength - 1].text) {
                    this.showBkMessage('前一条内容为空')
                } else {
                    // 不为空就添加一条空内容
                    const newobj = { 'text': '', 'cost': 0, 'isPrivate': this.allPrivate, '$index': contentLength }
                    this.renderList.dailyDataContent[index].content.push(newobj)
                }
            },
            // 删除表格中的一行内容
            deleteContent (row, removeIndex) {
                this.renderList.dailyDataContent[removeIndex]['content'].splice(row.$index, 1)
                for (const itemContent of this.renderList.dailyDataContent[removeIndex]['content']) {
                    if (row.$index < itemContent.$index) {
                        itemContent.$index--
                    }
                }
            },
            // 保存日报
            saveDaily () {
                let hasSomeContentEmpty = false
                const emptyContent = []
                this.newPostDaily.date = moment(this.formatDate).format(moment.HTML5_FMT.DATE)
                for (const index in this.renderList.dailyDataContent) {
                    this.renderList.dailyDataContent[index].title = this.renderList.dailyDataTitle[index]
                }
                for (const tableContent of this.renderList.dailyDataContent) {
                    const contentLength = tableContent.content.length
                    if (contentLength) {
                        if (!tableContent.content[contentLength - 1].text) {
                            hasSomeContentEmpty = true
                            emptyContent.push(tableContent.title + '最后一条')
                        } else {
                            for (const tableContentItem of tableContent.content) {
                                // 时间不填都是0
                                if (tableContentItem.cost === null || tableContentItem.cost === '' || tableContentItem.cost === undefined) {
                                    tableContentItem.cost = 0
                                }
                                tableContentItem.cost = parseFloat(tableContentItem.cost)
                            }
                            this.newPostDaily.content.push(tableContent)
                        }
                    } else {
                        hasSomeContentEmpty = true
                        emptyContent.push(tableContent.title)
                    }
                }
                for (const textContent of this.renderList.newTemplateContent) {
                    if (!textContent.text.length) {
                        hasSomeContentEmpty = true
                        emptyContent.push(textContent.title)
                    }
                    this.newPostDaily.content.push(textContent)
                }
                if (!hasSomeContentEmpty) {
                    // 保存
                    setUpdateDaily(this.newPostDaily).then(res => {
                        this.hasWrittenToday = true
                        this.newPostDaily = {
                            date: null,
                            content: [],
                            template_id: 0,
                            send_email: false
                        }
                        this.showBkMessage(res.message, 'success')
                    })
                } else {
                    this.showBkMessage(emptyContent.join(',') + ' 内容为空！')
                    this.newPostDaily.content = []
                }
            },
            moreTemplateDialogChange (val) {
                if (val === false) {
                    this.newTitle = ''
                }
            },
            // 获取请假管理表
            getLeaveList (sign) {
                const groupId = this.selectedGroup
                if (sign === null || sign === undefined) {
                    sign = 0 // 1 返回未请假人 或 0 返回请假人 或 2 返回个人所有请假信息
                }
                if (groupId === -1) {
                    this.showBkMessage('用户当前未加入任何组，无请假信息。')
                } else {
                    this.isleaveTableLoad = true
                    this.leaveTableData.data = []
                    const todayDate = moment(new Date()).format(moment.HTML5_FMT.DATE)
                    selectPerMsg(groupId, todayDate, sign).then(res => {
                        if (res.result) {
                            if (res.data.length !== null && res.data.length !== 0) {
                                // 设置请假日期选择栏禁用日期
                                if (sign === 2) {
                                    this.setLeavThDate(res.data)
                                } else if (sign === 0) {
                                    // 请假人的信息
                                    this.leaveRender(res.data)
                                }
                            }
                        } else {
                            this.showBkMessage(res.message)
                        }
                    }).finally(() => {
                        this.isleaveTableLoad = false
                    })
                }
            },
            // 设置请假日期（哪些是请过假的）
            setLeavThDate (data) {
                this.curUserLeaveList = data
                this.customLeaveOption = {
                    disabledDate: (date) => {
                        const nowDate = new Date()
                        if (date < nowDate.setHours(nowDate.getHours() - 24)) {
                            return true
                        } else {
                            let iscompareDateShow = true
                            this.curUserLeaveList.map((item, index) => {
                                // 选中的时间
                                const compareDate = moment(date).format('YYYY-MM-DD')
                                const startDate = moment(item[0]).format('YYYY-MM-DD')
                                const endDate = moment(item[1]).format('YYYY-MM-DD')
                                if (moment(startDate).isSameOrBefore(compareDate, 'day') && moment(compareDate).isSameOrBefore(endDate, 'day')) {
                                    iscompareDateShow = false
                                }
                            })
                            return !iscompareDateShow
                        }
                    }
                }
            },
            // 用户渲染请假的信息
            leaveRender (data) {
                // 渲染请假人信息
                this.timeSort(data).map((item, index) => {
                    this.leaveTableData.data.push({
                        'offdayId': item.off_info.id,
                        'start_date': item.off_info.start_date,
                        'end_date': item.off_info.end_date,
                        'reason': item.off_info.reason,
                        'info': item.username + item.name,
                        'username': item.username,
                        'name': item.name
                    })
                })
            },
            // 请假滑窗关闭事件
            hiddenSlider () {
                this.leaveFormData.reason = ''
                this.leaveFormData.dateTimeRange = [new Date(), new Date()]
                this.activeTabTitle = '请假申请'
            },
            // 切换请假页签事件
            changeTab (title) {
                this.activeTabTitle = title
                if (this.activeTabTitle === '请假信息') {
                    this.getLeaveList()
                    this.getLeaveList(2)
                }
            },
            // 选择组
            handleSelectGroup () {
                this.getLeaveList()
                this.getLeaveList(2)
            },
            // 清空请假日期
            clearDate () {
                this.leaveFormData.dateTimeRange = -1
            },
            // 请假确认事件(点击提交请假)
            submitLeave () {
                if (this.leaveFormData.reason === '') {
                    this.showBkMessage('请填写请假原因')
                    return
                }
                const params = {}
                params.start_date = moment(this.leaveFormData.dateTimeRange[0]).format(moment.HTML5_FMT.DATE)
                params.end_date = moment(this.leaveFormData.dateTimeRange[1]).format(moment.HTML5_FMT.DATE)
                params.reason = this.leaveFormData.reason
                applyRest(params).then(res => {
                    if (res.result) {
                        this.showBkMessage(res.message, 'success')
                        this.getLeaveList(2)
                    } else {
                        this.showBkMessage(res.message)
                    }
                })
            },
            // 请假管理按钮点击事件
            clickLeaveManage () {
                this.leaveSetting.visible = true
                this.getLeaveList(2)
            },
            // 花费时间为空时 默认为0
            checkSpendTime (value, index) {
                if (!value) {
                    this.renderList.dailyDataContent[0].content[index].cost = 0
                }
            },
            // 删除请假信息
            removeLeave (row) {
                const groupId = this.selectedGroup
                const offdayId = row.offdayId
                if (groupId === -1) {
                    this.showBkMessage('用户当前未加入任何组，无请假信息可删除。')
                } else {
                    this.$bkInfo({
                        title: '确认删除该请假信息？',
                        confirmLoading: true,
                        confirmFn: () => {
                            removeOff(groupId, offdayId).then(res => {
                                if (res.result) {
                                    this.showBkMessage(res.message, 'success')
                                    this.getLeaveList()
                                    this.getLeaveList(2)
                                } else {
                                    this.showBkMessage(res.message)
                                }
                            })
                        }
                    })
                }
            },
            // 请假时间排序
            timeSort (rankDate) {
                return rankDate.sort((a, b) => {
                    if (b.off_info.start_date > a.off_info.start_date) {
                        return -1
                    }
                    if (b.off_info.start_date < a.off_info.start_date) {
                        return 1
                    }
                })
            },
            // 弹窗
            showBkMessage (msg, theme = 'warning', delay = 2000) {
                const option = {
                    'offsetY': 80,
                    'delay': delay,
                    'theme': theme,
                    'message': msg
                }
                this.$bkMessage(option)
            },
            // 监听文本框内容的变化
            textChange (item, index, i) {
                this.deleteContent(item, index)
            },
            changeNumber (item, index, i, el) {
                if (el < 0) {
                    item.cost = 0
                }
                if (el > 24) {
                    item.cost = 24
                    el = 24
                }
            }
        }
    }
</script>

<style src='./index.css' scoped></style>
