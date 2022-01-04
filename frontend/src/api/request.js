import * as groupApi from './group/index.js'
import * as userApi from './user/index.js'

export default {
    ...groupApi,
    ...userApi
}
