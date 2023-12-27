<template>
	<Dialog
		:options="{ title: `Hoàn tất hóa đơn chưa thanh toán` }"
		modelValue="show"
	>
		<template #body-content>
			<div class="prose text-base">
				Bạn có hóa đơn chưa thanh toán trong tài khoản của mình cho các kỳ sau
				đây:
				<ul class="pt-2">
					<li
						class="font-semibold"
						v-for="invoice in $resources.unpaidInvoices.data"
					>
						{{
							$date(invoice.period_end).toLocaleString({
								month: 'long',
								year: 'numeric'
							})
						}}
						-
						{{ invoice.amount_due + ' VND' }}
					</li>
				</ul>
				Vui lòng hoàn tất và thanh toán các hóa đơn trước khi xóa tất cả các
				phương thức thanh toán hoặc tắt tài khoản. Bạn có thể kiểm tra chi tiết
				hóa đơn và thực hiện thanh toán từ
				<Link to="/billing/invoices/">tại đây</Link>. Có thể mất đến 2 giờ để
				thanh toán được cập nhật trong các hóa đơn của bạn.
			</div>
		</template>
		<template #actions>
			<Button
				variant="solid"
				class="w-full"
				@click="$resources.finalizeInvoices.submit()"
			>
				Hoàn tất hóa đơn
			</Button>
		</template>
	</Dialog>
</template>

<script>
export default {
	name: 'FinalizeInvoicesDialog',
	props: {
		show: Boolean,
		msg: String
	},
	resources: {
		finalizeInvoices: {
			url: 'press.api.billing.finalize_invoices'
		},
		unpaidInvoices: {
			url: 'press.api.billing.unpaid_invoices',
			auto: true
		}
	}
};
</script>
