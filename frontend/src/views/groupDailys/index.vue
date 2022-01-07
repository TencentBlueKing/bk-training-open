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
            <router-view></router-view>
        </keep-alive>
    </div>
</template>

<script>
    import { bkSelect, bkOption } from 'bk-magic-vue'
    import TabBtn from '@/components/TabBtn/index.vue'
    import requestApi from '@/api/request.js'
    const { getallGroups } = requestApi
    export default {
        components: {
            bkSelect,
            bkOption,
            TabBtn
        },
        data () {
            return {
                tabBtncontent: ['小组日报', '优秀日报'],
                groupList: [],
                panels: [
                    { name: 1, label: '' },
                    { name: 2, label: '' }
                ],
                active: this.$route.path.includes('/group-dailys/groupDaily') ? 1 : 2
            }
        },
        created () {
            getallGroups().then(res => {
                this.groupList = res.data
                if (window.location.search !== '') {
                    // 外面跳过来的
                    this.takeGroupuser()
                } else {
                    this.selectGroup = res.data[0].id
                    this.$store.commit('groupDaily/setCurGroupID', res.data[0].id)
                }
            })
        },
        methods: {
            changeType (type) {
                this.active = type
                const url = type === 1 ? `/group-dailys/groupDaily` : `/group-dailys/excellentDaily/${this.selectGroup}`
                this.$router.push(url)
            },
            changeGroup (val) {
                this.selectGroup = val
                window.localStorage.setItem('firstGroup', val)
                // 自己的跳转
                this.$store.commit('groupDaily/setCurGroupID', val)
            },
            // 跳转到的 组下的人
            takeGroupuser () {
                // 跳转过来的
                window.location.href.replace(/group=(.+)&username=(.+)/g, (_, $1, $2) => {
                    this.selectGroup = $1
                    // 外来链接的跳转
                    this.$store.commit('groupDaily/setCurGroupID', 'P' + $1)
                    this.$store.commit('groupDaily/setselectUserId', $2)
                })
            }
        }

    }
</script>

<style >
    @import url('./index.css');
</style>
