/**
 * 日报查看
 * */
const groupDaily = {
    namespaced: true,
    state: {
        curGroupID: null,
        selectUserId: null
    },
    mutations: {
        setGroupID (state, val) {
            state.curGroupID = val
        },
        setselectUserId (state, val) {
            state.selectUserId = val
        }
    },
    actions: {}
}

export default groupDaily
