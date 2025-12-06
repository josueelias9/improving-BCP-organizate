import { Suspense } from 'react'
import TransactionsTable from '@/app/ui/dashboard/transactions-table'
import { lusitana } from '@/app/ui/fonts'

export default async function TransactionsPage() {
    return (
        <main>
            <h1 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>
                Transactions
            </h1>
            <div className='mt-6 grid grid-cols-1 gap-6'>
                <Suspense fallback={<div>Loading transactions...</div>}>
                    <TransactionsTable />
                </Suspense>
            </div>
        </main>
    )
}
