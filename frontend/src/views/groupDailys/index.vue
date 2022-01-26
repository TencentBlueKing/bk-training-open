<template>
    <div class="groupDailys">
        <div class="groupDailys-btn">
            <div><bk-select
                :disabled="false"
                v-model="selectGroup"
                @selected="changeGroup"
                style="width: 250px;"
                ext-cls="selectgroup"
                :clearable="false"
                behavior="simplicity"
                searchable>
                <bk-option v-for="option in groupList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select></div>
            <!-- 小组日报 / 优秀日报 -->
            <TabBtn @changeType="changeType" :content="tabBtncontent" :active="active"></TabBtn>
        </div>
        <keep-alive>
            <component :is="curComponents" :curgroupid="selectGroup" :adminlist="AdminList" :groupusers="renderUser" :curdate="date" :username="username"></component>
        </keep-alive>
    </div>
</template>

<script>
    import { bkSelect, bkOption } from 'bk-magic-vue'
    import TabBtn from '@/components/TabBtn/index.vue'
    import GroupDaily from '@/components/GroupDailys/GroupDaily'
    import ExcellentDaily from '@/components/GroupDailys/ExcellentDaily'
    import requestApi from '@/api/request.js'
    import { setCurGroup, getCurGroup } from '@/utils/index.js'
    const { getallGroups, getGroupUsers, getGroupInfo } = requestApi
    export default {
        components: {
            bkSelect,
            bkOption,
            TabBtn,
            GroupDaily,
            ExcellentDaily
        },
        data () {
            return {
                // 当前选中的组
                selectGroup: null,
                // 当前活着的组件
                curComponents: 'GroupDaily',
                tabBtncontent: ['小组日报', '优秀日报'],
                groupList: [],
                active: 'first',
                // 用户
                renderUser: null,
                // 管理员
                AdminList: null
            }
        },
        watch: {
            selectGroup (oldval) {
                this.filterAdmin().then(res => {
                    // res就是管理员
                    this.AdminList = res
                    this.renderUserList(res)
                })
            }
        },
        activated () {
            this.setCurGroup = 0
            this.initRender()
        },
        methods: {
            initRender () {
                getallGroups().then(res => {
                    if (res.data.length !== 0) {
                        if (getCurGroup() !== 'null') {
                            this.selectGroup = getCurGroup()
                            getGroupInfo(this.selectGroup).then(res1 => {
                                // 本地有但是被管理员删了 变为第一组
                                if (!res1.result) {
                                    this.selectGroup = res.data[0].id
                                    setCurGroup(res.data[0].id)
                                }
                            })
                        } else {
                            this.selectGroup = res.data[0].id
                            setCurGroup(res.data[0].id)
                        }
                        this.groupList = res.data
                        this.filterAdmin().then(res => {
                            // res就是管理员
                            this.AdminList = res
                            this.renderUserList(res)
                        })
                        this.takeGroupuser()
                    } else {
                        this.$router.push('/my-group')
                    }
                })
            },
            changeType (type) {
                this.active = type
                // 控制小组日报 还是 优秀日报
                this.curComponents = type === 'first' ? 'GroupDaily' : 'ExcellentDaily'
            },
            changeGroup (val) {
                this.selectGroup = val
                setCurGroup(val)
            },
            // 获得管理员
            filterAdmin () {
                return new Promise((resolve, reject) => {
                    this.groupList.forEach(groupItem => {
                        if (Number(groupItem.id) === Number(this.selectGroup)) {
                            resolve(groupItem.admin)
                        }
                    })
                })
            },
            // 渲染的用户
            renderUserList (adminList) {
                getGroupUsers(this.selectGroup).then(res => {
                    // 过滤出不是管理员的数据
                    this.renderUser = res.data.filter(item => !adminList.includes(item.username))
                })
            },
            // 跳转到的 组下的人
            takeGroupuser () {
                // 跳转过来的
                if (this.$route.query.group !== undefined && this.$route.query.username !== undefined) {
                    this.selectGroup = this.$route.query.group
                    setCurGroup(this.$route.query.group)
                    this.username = this.$route.query.username
                }
                if (this.$route.query.group !== undefined && this.$route.query.date !== undefined) {
                    this.selectGroup = this.$route.query.group
                    setCurGroup(this.$route.query.group)
                    this.date = this.$route.query.date
                }
            }
        }
    }
</script>

<style >
    @import url('./index.css');
</style>
