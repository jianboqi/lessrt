#include <mitsuba/render/util.h>
#include <mitsuba/core/sched.h>
MTS_NAMESPACE_BEGIN


class ROT13WorkUnit :public WorkUnit
{
public:
	void set(const WorkUnit *workUnit){
		const ROT13WorkUnit *wu =
			static_cast<const ROT13WorkUnit *>(workUnit);
		m_char = wu->m_char;
		m_pos = wu->m_pos;
	}

	void load(Stream *stream) {
		m_char = stream->readChar();
		m_pos = stream->readInt();
	}
	
	void save(Stream *stream) const {
		stream->writeChar(m_char);
		stream->writeInt(m_pos);
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "ROT13WorkUnit[" << endl
			<< " char = '" << m_char << "'," << endl
			<< " pos = " << m_pos << endl
			<< "]";
		return oss.str();
	}

	inline char getChar() const { return m_char; }
	inline void setChar(char value) { m_char = value; }
	inline int getPos() const {return m_pos;}
	inline void setPos(int value) { m_pos = value; }

	MTS_DECLARE_CLASS()
private:
	char m_char;
	int m_pos;
};
MTS_IMPLEMENT_CLASS(ROT13WorkUnit, false, WorkUnit)


class ROT13WorkResult :public WorkResult
{
public:

	void load(Stream *stream) {
		m_char = stream->readChar();
		m_pos = stream->readInt();
	}

	void save(Stream *stream) const {
		stream->writeChar(m_char);
		stream->writeInt(m_pos);
	}

	std::string toString() const {
		std::ostringstream oss;
		oss << "ROT13WorkUnit[" << endl
			<< " char = '" << m_char << "'," << endl
			<< " pos = " << m_pos << endl
			<< "]";
		return oss.str();
	}

	inline char getChar() const { return m_char; }
	inline void setChar(char value) { m_char = value; }
	inline int getPos() const { return m_pos; }
	inline void setPos(int value) { m_pos = value; }

	MTS_DECLARE_CLASS()
private:
	char m_char;
	int m_pos;
};
MTS_IMPLEMENT_CLASS(ROT13WorkResult, false, WorkResult)


class ROT13WorkProcessor : public WorkProcessor {
public:
	/// Construct a new work processor
	ROT13WorkProcessor() : WorkProcessor() { }
	/// Unserialize from a binary data stream (nothing to do in our case)
	ROT13WorkProcessor(Stream *stream, InstanceManager *manager)
		: WorkProcessor(stream, manager) { }
	/// Serialize to a binary data stream (nothing to do in our case)
	void serialize(Stream *stream, InstanceManager *manager) const {
		
	}

	ref<WorkUnit> createWorkUnit() const {
		return new ROT13WorkUnit();
	}
	ref<WorkResult> createWorkResult() const {
		return new ROT13WorkResult();
	}
	ref<WorkProcessor> clone() const {
		return new ROT13WorkProcessor(); // No state to clone in our case
	}
	/// No internal state, thus no preparation is necessary
	void prepare() { }
	/// Do the actual computation
	void process(const WorkUnit *workUnit, WorkResult *workResult,
		const bool &stop) {
		const ROT13WorkUnit *wu
			= static_cast<const ROT13WorkUnit *>(workUnit);
		ROT13WorkResult *wr = static_cast<ROT13WorkResult *>(workResult);
		wr->setPos(wu->getPos());
		wr->setChar((std::toupper(wu->getChar()) - 'A' + 13) % 26 + 'A');
	}
	MTS_DECLARE_CLASS()
};
MTS_IMPLEMENT_CLASS_S(ROT13WorkProcessor, false, WorkProcessor)


class ROT13Process : public ParallelProcess {
public:
	ROT13Process(const std::string &input) : m_input(input), m_pos(0) {
		m_output.resize(m_input.length());
	}
	ref<WorkProcessor> createWorkProcessor() const {
		return new ROT13WorkProcessor();
	}
	std::vector<std::string> getRequiredPlugins() {
		std::vector<std::string> result;
		result.push_back("rot13");
		return result;
	}
	EStatus generateWork(WorkUnit *unit, int worker /* unused */) {
		if (m_pos >= (int)m_input.length())
			return EFailure;
		ROT13WorkUnit *wu = static_cast<ROT13WorkUnit *>(unit);
		wu->setPos(m_pos);
		wu->setChar(m_input[m_pos++]);
		return ESuccess;
	}
	void processResult(const WorkResult *result, bool cancelled) {
		if (cancelled) // indicates a work unit, which was
			return; // cancelled partly through its execution
		const ROT13WorkResult *wr =
			static_cast<const ROT13WorkResult *>(result);
		m_output[wr->getPos()] = wr->getChar();
	}
	inline const std::string &getOutput() {
		return m_output;
	}
	MTS_DECLARE_CLASS()
public:
	std::string m_input;
	std::string m_output;
	int m_pos;
};
MTS_IMPLEMENT_CLASS(ROT13Process, false, ParallelProcess)



class ROT13Encoder : public Utility {
public:
	int run(int argc, char **argv) {
		if (argc < 2) {
			cout << "Syntax: mtsutil rot13 <text>" << endl;
			return -1;
		}
		ref<ROT13Process> proc = new ROT13Process(argv[1]);
		ref<Scheduler> sched = Scheduler::getInstance();
		/* Submit the encryption job to the scheduler */
		sched->schedule(proc);
		/* Wait for its completion */
		sched->wait(proc);
		cout << "Result: " << proc->getOutput() << endl;
	}
	MTS_DECLARE_UTILITY()
};
MTS_EXPORT_UTILITY(ROT13Encoder, "Perform a ROT13 encryption of a string")
MTS_NAMESPACE_END