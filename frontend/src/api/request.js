import * as groupApi from './group/index.js'
import * as userApi from './user/index.js'
import * as dailyApi from './daily/index.js'

export default {
    ...groupApi,
    ...userApi,
    ...dailyApi
}
