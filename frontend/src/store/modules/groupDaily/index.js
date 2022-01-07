/**
 * 日报查看
 * */
const groupDaily = {
    namespaced: true,
    state: {
        curGroupID: null,
        curUserID: null
    },
    mutations: {
        // 日报查看 当前组Id
        setCurGroupID (state, val) {
            state.curGroupID = val
        },
        // 跳转要查询的人
        setselectUserId (state, val) {
            state.curUserID = val
        }
    },
    actions: {}
}

export default groupDaily
