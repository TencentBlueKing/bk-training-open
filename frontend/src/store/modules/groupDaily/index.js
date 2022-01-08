/**
 * 日报查看
 * */
const groupDaily = {
    namespaced: true,
    state: {
        curGroupID: null,
        selectUserId: null,
        curDate: null,
        // 当前组的管理员
        adminList: [],
        // 普通用户
        ordinary: []
    },
    mutations: {
        setGroupID (state, val) {
            state.curGroupID = val
        },
        setselectUserId (state, val) {
            state.selectUserId = val
        },
        setDate (state, val) {
            state.curDate = val
        },
        setAdminList (state, val) {
            state.adminList = val
        },
        setOrdinary (state, val) {
            state.ordinary = val
        }
    },
    actions: {}
}

export default groupDaily
