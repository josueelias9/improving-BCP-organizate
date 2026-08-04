import { Suspense } from 'react'
import TransactionsTable from '@/app/ui/dashboard/transactions/transactions-table'
import { lusitana } from '@/app/ui/fonts'

import { getTransactionsTransactionsGet } from '@/app/lib/orval/src/transactions/transactions'
import { getCategoriesCategoriesGet } from '@/app/lib/orval/src/categories/categories'

export default async function TransactionsPage() {
    const [transactionsResponse, categoriesResponse] = await Promise.all([
        getTransactionsTransactionsGet(),
        getCategoriesCategoriesGet()
    ])
    return (
        <main>
            <h1 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>Transactions</h1>
            <div className='mt-6 grid grid-cols-1 gap-6'>
                <Suspense fallback={<div>Loading transactions...</div>}>
                    {
                        // execute this only when response is successful
                        transactionsResponse.status === 200 && categoriesResponse.status === 200 ? (
                            <TransactionsTable
                                transactionsData={transactionsResponse.data}
                                categoriesData={categoriesResponse.data}
                            />
                        ) : null
                    }
                </Suspense>
            </div>
        </main>
    )
}
