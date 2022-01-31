import Axios from 'axios';

const ownCloudClient = Axios.create({
    baseURL: '/owncloud/api',
    withCredentials: true,
    headers: {
        "Accept": 'application/json',
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
})

// const apiClient = Axios.create({
//     baseURL: '/api',
//     withCredentials: true,
//     headers: {
//         Accept: 'application/json',
//         'Content-Type': 'application/json',
//         'Access-Control-Allow-Origin': '*'
//     }
// })

export default {
    sendMails(email) {
        return ownCloudClient.post('/', { email: email })
    },
}