<template>
    <!-- 我的小组 -->
    <div class="mygroup">
        <!-- 顶部组基本信息 -->
        <div class="group-msg">
            <div class="group-msg-groupname">
                <!-- 选择组 -->
                <bk-select
                    v-model="curGroupId"
                    style="width: 250px;"
                    behavior="simplicity"
                    @selected="changeGroup"
                    searchable
                    ext-cls="group-msg-curgroupid"
                    :clearable="false"
                >
                    <bk-option
                        v-for="option in AllgGroupsist"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name"
                    >
                    </bk-option>
                </bk-select>
            </div>
            <div class="group-msg-admin">
                <div class="group-msg-admin-title">管理员: </div>
                <div class="group-msg-admin-list">
                    <div
                        class="group-msg-admin-item"
                        v-for="(item, index) in curGroupData.admin_list"
                        :key="index"
                    >
                        {{ item.username }}({{ item.name }})
                        <span
                            style="backgroundColor: white"
                            v-if="index !== adminIDList.length - 1"
                        >&nbsp;/&nbsp;</span
                        >
                    </div>
                </div>
            </div>
            <!-- 对组的功能 -->
            <div class="group-func">
                <!-- 新增组 & 入组请求 -->
                <div class="group-func-major">
                    <bk-badge style="marginRight:5px" theme="danger" :max="99" :val=" newApplyData.length" :visible="newApplyData.length">
                        <bk-button
                            v-show="isAdmin"
                            theme="primary"
                            :hover-theme="'primary'"
                            @click="isshowSideslider = true">
                            处理申请
                        </bk-button>
                    </bk-badge>
                    <bk-button title="primary" :text="true" :hover-theme="'primary'"
                        class="group-func-major-item"
                        @click="executeFunc('addGroup', '新增组')">
                        新增小组
                    </bk-button>
                    <bk-button title="primary" :text="true" :hover-theme="'primary'" class="group-func-major-item" @click="executeFunc('applyJoinGroup', '请求入组')">
                        申请入组
                    </bk-button>
                    <bk-button v-show="isAdmin" :text="true" :hover-theme="'primary'"
                        class="group-func-major-item"
                        @click="executeFunc('compileGroup', '编辑组')">
                        编辑小组
                    </bk-button>
                    <bk-button v-show="isAdmin" :text="true" :hover-theme="'danger'" class="group-func-major-item" @click="delete_Group()">
                        删除小组
                    </bk-button>
                </div>
            </div>
        </div>
        <!-- 组内成员 -->
        <div class="group-member">
            <!-- 新增成员 & 批量删除 -->
            <div class="group-member-func" v-show="isAdmin">
                <bk-button ext-cls="group-member-func-add"
                    @click="executeFunc('addGroupUser', '新增成员')">
                    新增成员
                </bk-button>
                <bk-button ext-cls="group-member-func-batchdel" @click="alldeleteUsers">
                    批量删除
                </bk-button>
            </div>
            <!-- 成员List -->
            <div class="group-member-renderlist">
                <bk-table
                    :data="renderGroupUsers"
                    :size="size"
                    :pagination="pagination"
                    @selection-change="selecchange"
                    @page-change="handlePageChange"
                    @page-limit-change="LimitChange"
                >
                    <bk-table-column type="selection" width="60"></bk-table-column>
                    <bk-table-column
                        type="index"
                        label="序列"
                        width="60"
                    ></bk-table-column>
                    <bk-table-column label="用户名" prop="username"></bk-table-column>
                    <bk-table-column label="姓名" prop="name"></bk-table-column>
                    <bk-table-column label="电话" prop="phone"></bk-table-column>
                    <bk-table-column label="邮箱" prop="email"></bk-table-column>
                    <bk-table-column label="操作" width="150">
                        <template slot-scope="props">
                            <bk-button
                                class="mr10"
                                theme="primary"
                                text
                                :disabled="!isAdmin || curGroupData.admin.includes(props.row.username)"
                                @click="removeGroupUser(props.row)"
                            >移除</bk-button
                            >
                        </template>
                    </bk-table-column>
                </bk-table>
            </div>
        </div>
        <bk-dialog
            v-model="isshowDialog"
            theme="primary"
            :mask-close="false"
            :header-position="left"
            :auto-close="false"
            @confirm="dialogConfirm()"
            @cancel="dialogCancel()"
            :title="dialogTitle"
            class="group-dialog"
        >
            <!-- 如果是新增组 -->
            <div v-show="funcName === 'addGroup'">
                <bk-form label-width="120">
                    <bk-form-item label="组名称" required="true">
                        <bk-input v-model="newGroup"></bk-input>
                    </bk-form-item>
                    <bk-form-item label="管理员">
                        <bk-select
                            searchable
                            multiple
                            display-tag
                            v-model="selectAdminIDList"
                        >
                            <bk-option
                                v-for="user in AllUsers"
                                :key="user.id"
                                :id="user.id"
                                :name="user.username + '(' + user.display_name + ')'"
                            >
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                </bk-form>
            </div>
            <!-- 请求入组 -->
            <div v-show="funcName === 'applyJoinGroup'">
                <bk-form label-width="120">
                    <bk-form-item label="组名称" required="true">
                        <bk-select
                            searchable
                            multiple
                            display-tag
                            v-model="selectJoinGroup"
                        >
                            <bk-option
                                v-for="Group in NotJoinGroup"
                                :key="Group.id"
                                :id="Group.id"
                                :name="Group.group_name"
                            >
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                </bk-form>
            </div>
            <!-- 编辑组 -->
            <div v-show="funcName === 'compileGroup'">
                <bk-form label-width="120">
                    <bk-form-item label="组名称" required="true">
                        <bk-input v-model="curGroupData.name"></bk-input>
                    </bk-form-item>
                    <bk-form-item label="管理员">
                        <bk-select
                            searchable
                            multiple
                            display-tag
                            v-model="selectCompileadminID"
                        >
                            <bk-option
                                v-for="user in AllUsers"
                                :key="user.id"
                                :id="user.id"
                                :name="user.username + '(' + user.display_name + ')'"
                            >
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                </bk-form>
            </div>
            <!-- 新增成员 -->
            <div v-show="funcName === 'addGroupUser'">
                <bk-form label-width="120">
                    <bk-form-item label="新成员" required="true">
                        <bk-select
                            searchable
                            multiple
                            display-tag
                            v-model="selectnotakeUsersID"
                        >
                            <bk-option
                                v-for="user in notakeUsers"
                                :key="user.id"
                                :id="user.id"
                                :name="user.username + '(' + user.display_name + ')'"
                            >
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                </bk-form>
            </div>
        </bk-dialog>
        <!-- 同意申请入组的地方 -->
        <bk-sideslider :is-show.sync="isshowSideslider" :quick-close="true">
            <div slot="content" class="content-box">
                <h3>处理入组</h3>
                <bk-table
                    style="margin-top: 15px;"
                    :data="newApplyData"
                >
                    <bk-table-column prop="username" label="用户名" width="140"></bk-table-column>
                    <bk-table-column prop="name" label="姓名" width="110"></bk-table-column>
                    <bk-table-column label="操作" width="50">
                        <template slot-scope="props">
                            <bk-button
                                class="mr10"
                                theme="primary"
                                text
                                @click="dealNewApply(props.row,1)">
                                同意
                            </bk-button>
                            <bk-button
                                class="mr10"
                                theme="primary"
                                text
                                @click="dealNewApply(props.row,2)">
                                拒绝
                            </bk-button>
                        </template>
                    </bk-table-column>
                </bk-table>
            </div>
        </bk-sideslider>
    </div>
</template>

<script>
    import { isAdmin, setCurGroup, getCurGroup } from '@/utils/index.js'
    import {
        bkSelect,
        bkOption,
        bkDialog,
        bkTable,
        bkTableColumn,
        bkButton
    } from 'bk-magic-vue'
    import requestApi from '@/api/request.js'
    const { getallGroups,
            getGroupInfo,
            getAllUsers,
            getUser,
            addGroup,
            getNotJoinGroup,
            deleteGroup,
            getGroupUsers,
            addGroupUsers,
            deleteGroupUsers,
            updateGroup,
            ApplyJoinGroup,
            dealJoinGroup } = requestApi
            
    export default {
        components: {
            bkSelect,
            bkOption,
            bkDialog,
            bkTable,
            bkTableColumn,
            bkButton
        },
        data () {
            return {
                // 我是不是管理员
                isAdmin: '',
                // 当前选择的用户组
                curGroupId: '',
                // 所有用户组列表
                AllgGroupsist: [],
                // 当前渲染的组 基本数据
                curGroupData: [],
                // 蓝鲸所有用户 (作为管理员的候选人)
                AllUsers: [],
                // 是否展示对话框
                isshowDialog: false,
                // 对话框标题
                dialogTitle: '',
                // 选中了哪些人作为管理员ID
                selectAdminIDList: [],
                // 选中了哪些人作为管理员数据
                selectAdminList: [],
                // 新增的组名
                newGroup: '',
                // 本人信息
                myMsg: {},
                // 不可以操作的组 (就是我为加入 & 我又不是管理员)
                NotJoinGroup: [],
                // 我要加入的组
                selectJoinGroup: [],
                // 编辑选中的管理员ID,
                selectCompileadminID: [],
                selectCompileadminList: [],
                // 小组成员数据全部
                groupUsers: [],
                // 成员表格 多选的数据
                tableSelect: [],
                funcName: '',
                // 选择未参与的用户
                size: 'small',
                // 新增成员id
                selectnotakeUsersID: [],
                // 分页器配置
                pagination: {
                    current: 1,
                    count: 100,
                    limit: 10
                },
                // 入组请求
                newApplyData: [],
                // 是否展示侧栏(入组申请)
                isshowSideslider: false
            }
        },
        computed: {
            dialogConfirm () {
                let selectFunc = function () {}
                if (this.funcName === 'addGroup') {
                    selectFunc = this.confirmAdd
                } else if (this.funcName === 'applyJoinGroup') {
                    selectFunc = this.confirmApplyJoinGroup
                } else if (this.funcName === 'compileGroup') {
                    selectFunc = this.compileGroup
                } else if (this.funcName === 'addGroupUser') {
                    selectFunc = this.compileaddGroupUser
                }
                return selectFunc
            },
            dialogCancel () {
                let selectFunc = function () {}
                if (this.funcName === 'addGroup') {
                    selectFunc = this.cancelAdd
                } else if (this.funcName === 'applyJoinGroup') {
                    selectFunc = this.cancelApplyJoinGroup
                } else if (this.funcName === 'compileGroup') {
                    selectFunc = this.cancelcompileGroup
                } else if (this.funcName === 'addGroupUser') {
                    selectFunc = this.canceladdGroupUser
                }
                return selectFunc
            },
            // 分页切割
            renderGroupUsers () {
                return this.groupUsers.slice(
                    (this.pagination.current - 1) * this.pagination.limit,
                    this.pagination.current * this.pagination.limit)
            },
            // 管理员List
            adminIDList () {
                return (this.curGroupData.admin_list !== undefined && this.curGroupData.admin_list.map((item) => item.id)) || []
            },
            // 过滤出没有在组里面的成员
            notakeUsers () {
                const GroupUserID = this.groupUsers.map((item) => item.id)
                // 未参与的用户
                return this.AllUsers.filter((item) => {
                    if (!GroupUserID.includes(item.id)) {
                        return item
                    }
                })
            },
            // 判断删除人员中有无管理员
            existAdmin () {
                let flat = true
                if (this.tableSelect.length === 0) {
                    this.handleBox('error', '未选中成员')
                    flat = false
                }
                this.adminIDList
                    .forEach((id) => {
                        if (this.tableSelect && this.tableSelect.map((item) => item.id).includes(id)) {
                            // 删除人员中有管理员
                            this.handleBox('error', '不能选择删除管理员')
                            flat = false
                        }
                    })
                return flat
            }
        },
        activated () {
            // 缓解切换时组名抖动问题
            if (this.curGroupId !== getCurGroup()) {
                this.curGroupId = null
            }
            // 获得本人信息
            getUser().then((res) => {
                this.myMsg = res.data
            })
            // 获得蓝鲸用户的数据(所有用户) 缓存 & 重新获取
            if (JSON.parse(localStorage.getItem('AllUsers')) !== null) {
                this.AllUsers = JSON.parse(localStorage.getItem('AllUsers'))
            } else {
                getAllUsers().then((res) => {
                    this.AllUsers = res
                })
            }
            // 初始化第一组
            this.initGroup()
            // 获得未加入的组
            getNotJoinGroup().then((res) => {
                this.NotJoinGroup = res
            })
        },
        methods: {
            // 初始化选中第一组 flat 为true我就不走缓存 强制请求 选中第一组
            initGroup (flat = false) {
                getallGroups().then((res) => {
                    if (res.data.length !== 0) {
                        // 有权限管理的所欲组
                        this.AllgGroupsist = res.data
                        // 本地有就用本地
                        if (getCurGroup() !== null && !flat) {
                            this.curGroupId = getCurGroup()
                            this.getGroupInfoData(getCurGroup())
                        } else {
                            // 没有就是第一组 并且存储本地
                            this.curGroupId = res.data[0].id
                            setCurGroup(res.data[0].id)
                            this.getGroupInfoData(res.data[0].id)
                        }
                        this.selectCompileadminID = this.adminIDList
                    } else {
                        // 如果没有第一组
                        this.curGroupData = []
                        this.curGroupId = ''
                        setCurGroup(null)
                        this.groupUsers = []
                        this.AllgGroupsist = []
                    }
                    this.loadApply()
                })
            },
            //  跟换组
            changeGroup (curGroupId) {
                this.curGroupId = curGroupId
                setCurGroup(curGroupId)
                this.getGroupInfoData(curGroupId)
                this.loadApply()
            },
            // 获得组的基本数据 & 调用更新成员列表
            getGroupInfoData (curGroupId) {
                getGroupInfo(curGroupId).then((res) => {
                    // 我给被管理员删了但我本地还有就要换组
                    if (!res.result) {
                        this.initGroup(true)
                    }
                    this.curGroupData = res.data
                    this.isAdmin = isAdmin(this.myMsg.username, res.data.admin)
                    // 更新列表数据 & 排序
                    this.updateRender(curGroupId)
                })
            },
            // 执行对组/ 成员 的操作 根据不同的funcName进行不同操作
            executeFunc (funcName, Title) {
                if (funcName === 'compileGroup') {
                    this.selectCompileadminID = this.adminIDList
                    this.getadminMsg()
                }
                this.isshowDialog = true
                // 是谁执行了这个方法 把弹出框打开就渲染对应的东西
                this.funcName = funcName
                this.dialogTitle = Title
            },
            // 确认添加组
            confirmAdd () {
                // 内容没选
                if (this.newGroup === '') {
                    this.handleBox('error', '请补全内容')
                    return
                }
                // 自己也需要加到管理员里面
                this.myMsg.display_name = this.myMsg.name
                this.selectAdminList.unshift(this.myMsg)
                // id 转化为需要的admin
                this.AllUsers.forEach((user) => {
                    if (this.selectAdminIDList.includes(user.id) && user.id !== this.myMsg.id) {
                        this.selectAdminList.push(user)
                    }
                })
                addGroup({ name: this.newGroup, admin: this.selectAdminList }).then(
                    (res) => {
                        this.handleBox('success', '添加成功')
                        this.isshowDialog = false
                        // 获取全部组
                        getallGroups().then((res1) => {
                            this.AllgGroupsist = res1.data
                            this.changeGroup(res.data.group_id)
                        })
                    }
                )
                this.clearAddInput()
            },
            // 取消添加组
            cancelAdd () {
                this.clearAddInput()
            },
            // 清空添加组的input数据
            clearAddInput () {
                this.newGroup = ''
                this.selectAdminIDList = []
                this.selectAdminList = []
            },
            // 提示框
            handleBox (type, title) {
                const config = type === 'success' ? { offsetY: 80, message: title, theme: 'success' } : { offsetY: 80, message: title, theme: 'error' }
                this.$bkMessage(config)
            },
            // 确定申请入组
            async confirmApplyJoinGroup () {
                const applyArr = [...this.selectJoinGroup]
                Promise.all([
                    ...applyArr.map((item) => {
                        return ApplyJoinGroup({ group_id: item })
                    })
                ]).then((res) => {
                    getNotJoinGroup().then((res) => {
                        this.selectJoinGroup = []
                        this.NotJoinGroup = res
                        this.isshowDialog = false
                        // 申请成功
                        this.handleBox('success', '申请成功')
                    })
                })
            },
            // 取消申请入组
            cancelApplyJoinGroup () {
                this.selectJoinGroup = []
            },
            // 确定编辑组
            compileGroup () {
                // 重新根据id 确定选了哪几个管理员
                this.getadminMsg()
                if (!this.selectCompileadminID.includes(this.myMsg.id)) {
                    this.selectCompileadminList.push(this.myMsg)
                }
                updateGroup(this.curGroupId, {
                    name: this.curGroupData.name,
                    admin: this.selectCompileadminList
                }).then((res) => {
                    this.handleBox('success', '编辑成功')
                    this.isshowDialog = false
                    this.selectCompileadminList = []
                    this.selectCompileadminID = []
                    getallGroups().then((res1) => {
                        this.AllgGroupsist = res1.data
                        this.changeGroup(this.curGroupId)
                    })
                })
            },
            // 根据id获取管理员用户数据
            getadminMsg () {
                this.selectCompileadminList = []
                this.AllUsers.forEach((item) => {
                    if (this.selectCompileadminID.includes(item.id)) {
                        this.selectCompileadminList.push(item)
                    }
                })
            },
            // 删除组
            delete_Group () {
                this.showBkInfo('确认要删除？', this.deleteCurGroup)
            },
            // 删除当前组
            deleteCurGroup () {
                deleteGroup(this.curGroupId).then((res) => {
                    if (res.result) {
                        // 初始化到第一组
                        this.initGroup()
                        this.handleBox('success', '删除成功')
                    } else {
                        this.handleBox('error', '删除失败')
                    }
                })
            },
            // 分页页数变化
            LimitChange (limit) {
                this.pagination.limit = limit
                this.pagination.current = 1
            },
            // 换页
            handlePageChange (newPage) {
                this.pagination.current = newPage
            },
            // 新增成员
            compileaddGroupUser () {
                if (this.selectnotakeUsersID.length !== 0) {
                    addGroupUsers(this.curGroupId, this.selectnotakeUsersID).then((res) => {
                        if (res.result) {
                            this.isshowDialog = false
                            this.selectnotakeUsersID = []
                            this.handleBox('success', '成员添加成功')
                            this.changeGroup(this.curGroupId)
                        }
                    })
                } else {
                    this.handleBox('error', '请先选择成员')
                }
            },
            // 取消新增成员
            canceladdGroupUser () {
                this.isshowDialog = false
                this.selectnotakeUsersID = []
            },
            // 删除组内成员
            removeGroupUser (row) {
                this.showBkInfo('确认删除该用户？', this.confirmDelete(row))
            },
            // 确认单删用户
            confirmDelete (row) {
                // 闭包 & 箭头函数
                return () => {
                    const deleteForm = { user_id: row.id }
                    deleteGroupUsers(this.curGroupId, deleteForm).then((res) => {
                        this.handleBox('success', '移除成功')
                        this.changeGroup(this.curGroupId)
                    })
                }
            },

            // 表格选项发生变化
            selecchange (val) {
                this.tableSelect = val
            },
            // 批量删除数据
            alldeleteUsers () {
                // 判断有没有选中管理员
                if (this.existAdmin) this.showBkInfo('确认要批量删除数据？', this.confirmAllDelete)
            },
            updateRender (curGroupId) {
                // 获得组成员 放里面等curGroupData 更新了才能排序
                getGroupUsers(curGroupId).then((res) => {
                    this.pagination.count = res.data.length
                    this.groupUsers = res.data.sort((a, b) => {
                        if ((this.adminIDList.includes(a.id) && this.adminIDList.includes(b.id)) || (this.adminIDList.includes(a.id) && !this.adminIDList.includes(b.id)) || (this.adminIDList.includes(a.id) && !this.adminIDList.includes(b.id))) {
                            return -1
                        }
                        return 1
                    })
                })
            },
            // 公共确认框
            showBkInfo (title, confirmFn) {
                this.$bkInfo({
                    title,
                    confirmFn
                })
            },
            // 确认批量删除
            confirmAllDelete () {
                Promise.all(
                    this.tableSelect
                        .map((item) => item.id)
                        .map((item2) => {
                            deleteGroupUsers(this.curGroupId, { user_id: item2 })
                        })
                ).then((res) => {
                    this.handleBox('success', `成功移除${res.length}个成员`)
                    // 列表视图更新
                    this.changeGroup(this.curGroupId)
                })
            },
            loadApply () {
                //  获取申请该组的列表
                this.$http.get(
                    '/get_apply_for_group_users/' + this.curGroupId + '/'
                ).then(res => {
                    this.newApplyData = res.data
                })
            },
            // 处理新的入组申请
            dealNewApply (row, status) {
                dealJoinGroup(this.curGroupId, { user_id: row.user_id, status: status }).then(res => {
                    if (res.result) {
                        for (const i in this.newApplyData) {
                            if (this.newApplyData[i].hasOwnProperty('user_id') && this.newApplyData[i].user_id === row.user_id) {
                                this.newApplyData.splice(i, 1)
                            }
                        }
                        this.getGroupInfoData(this.curGroupId)
                        this.handleBox('success', res.message)
                    } else {
                        this.handleBox('error', res.message)
                    }
                })
            }
        }
    }
</script>

<style scoped>
@import "./index.css";
</style>
