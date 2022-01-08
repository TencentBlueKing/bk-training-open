/**
 * 日报查看
 * */
const groupDaily = {
    namespaced: true,
    state: {
        curGroupID: null,
        selectUserId: null,
        curDate: null
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
        }
    },
    actions: {}
}

export default groupDaily
