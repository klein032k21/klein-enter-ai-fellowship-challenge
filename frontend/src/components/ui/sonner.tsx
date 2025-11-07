import { Toaster as Sonner } from "sonner"

type ToasterProps = React.ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
  return (
    <Sonner
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-card group-[.toaster]:text-white group-[.toaster]:border-white/10 group-[.toaster]:shadow-lg",
          description: "group-[.toast]:text-white/70",
          actionButton:
            "group-[.toast]:bg-primary group-[.toast]:text-black",
          cancelButton:
            "group-[.toast]:bg-muted group-[.toast]:text-white/70",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
